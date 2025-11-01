import os
import io
import json
import numpy as np
import pandas as pd
import boto3
import openai

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import EEGRecord
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def compute_basic_features(eeg_array):
    """Compute simple features from an EEG timeseries (1D list/array).
    Returns a dict of mean, std, and simple band approximations.
    """
    arr = np.asarray(eeg_array, dtype=float)
    df = pd.Series(arr)
    features = {
        'mean': float(df.mean()),
        'std': float(df.std()),
        'min': float(df.min()),
        'max': float(df.max()),
        'length': int(len(df)),
    }
    return features


def upload_to_s3(content_bytes, key):
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    bucket = settings.AWS_S3_BUCKET
    if not bucket:
        return None
    s3.put_object(Bucket=bucket, Key=key, Body=content_bytes)
    region = s3.get_bucket_location(Bucket=bucket).get('LocationConstraint') or ''
    url = f'https://{bucket}.s3.{region}.amazonaws.com/{key}' if region else f'https://{bucket}.s3.amazonaws.com/{key}'
    return url


def call_openai_infer(features):
    """Call OpenAI to get a simple mood inference from features.
    This is a helper; in production you'd build a robust prompt and handle errors/quotas.
    """
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return 'unknown (no-openai-key)'
    client = openai.OpenAI(api_key=api_key)
    prompt = f"Given EEG features {json.dumps(features)}, infer a likely mood (short label)."
    try:
        resp = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=16,
        )
        text = resp.choices[0].message.content.strip()
        return text
    except Exception as e:
        print(f"OpenAI error: {e}")
        return 'error'


class UploadEEGAPIView(APIView):
    """Receive EEG data (JSON) and process it: compute features, store in S3, and infer mood."""

    def post(self, request, format=None):
        data = request.data
        eeg = data.get('eeg')
        if eeg is None:
            return Response({'detail': 'eeg field required (array of numbers)'}, status=status.HTTP_400_BAD_REQUEST)

        features = compute_basic_features(eeg)

        # Save raw data to S3
        raw_bytes = json.dumps({'eeg': eeg}).encode('utf-8')
        key = f'raw/{EEGRecord.objects.count()+1}.json'
        s3_url = upload_to_s3(raw_bytes, key)

        mood = call_openai_infer(features)

        rec = EEGRecord.objects.create(raw_data_s3=s3_url, features=features, mood_inference=mood)

        # Notify websocket consumers
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('neurobot_live', {
            'type': 'eeg.processed',
            'record_id': rec.id,
            'features': features,
            'mood': mood,
        })

        return Response({'id': rec.id, 'mood': mood, 'features': features, 's3': s3_url})
