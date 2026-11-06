#!/bin/bash
echo "Starting AETHRIX - Original Independent AI Model"
echo "================================================"
python -c "
from aethrix.inference.engine import AethrixInference
from aethrix.core.config import AethrixConfig
print('Initializing AETHRIX...')
engine = AethrixInference(config=AethrixConfig())
print('AETHRIX ready!')
response = engine.chat('Hello, introduce yourself')
print(response)
"
