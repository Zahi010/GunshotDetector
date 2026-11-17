import pandas as pd
import json

eval_df = pd.read_csv('e:/FSD50K.dev_audio/FSD50K.ground_truth/eval.csv')
with open('e:/FSD50K.dev_audio/FSD50K.metadata/eval_clips_info_FSD50K.json') as f:
    clip_info = json.load(f)

vocab = pd.read_csv('e:/FSD50K.dev_audio/FSD50K.ground_truth/vocabulary.csv', names=['id', 'label', 'mid'])

classes = [
    'Gunshot_and_gunfire',
    'Fireworks',
    'Door',
    'Slam',
    'Glass',
    'Hammer',
    'Thunder',
    'Thunderstorm',
    'Explosion',
    'Motor_vehicle_(road)',
    'Car',
    'Truck',
    'Bus',
    'Motorcycle',
    'Siren',
    'Bark',
    'Crying_and_sobbing',
    'Cough',
    'Footsteps',
    'Wind',
    'Rain',
    'Water',
    'Chirp_and_tweet',
    'Waves_and_surf'
]

print("Class counts in eval.csv:")
for c in classes:
    m = eval_df[eval_df['labels'].str.contains(c, na=False)]
    print(f"  {c:25s}: {len(m)} files")

