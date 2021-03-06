#!/bin/sh
python create_query_data.py --length 2 3 5 6 10 --test_dir=data/test_data/fma_large --noise_dir=data/Noises_unsampled --ir_dir=data/IR_unsampled
python clean_data.py
python test.py --test_dir=data/test_data/fma_large --model_path=model/model_ver1_epoch_300.pth

# python create_query_data.py --length 10 --test_dir=data/test_data/fma_large --noise_dir=data/Noises_unsampled --ir_dir=data/IR_unsampled
# python test.py --fp_path=fingerprints/fma_large_ver3.pt --model_path=model/model_ver3_epoch_260.pth --query_dir=data/fma_large_1sec_2K --eval=True >> results/fma_large_1sec_2K.txt
# python test.py --fp_path=fingerprints/fma_large_ver3.pt --model_path=model/model_ver3_epoch_260.pth --query_dir=data/fma_large_2sec_2K --eval=True >> results/fma_large_2sec_2K.txt
# python test.py --fp_path=fingerprints/fma_large_ver3.pt --model_path=model/model_ver3_epoch_260.pth --query_dir=data/fma_large_3sec_2K --eval=True >> results/fma_large_3sec_2K.txt
# python test.py --fp_path=fingerprints/fma_large_ver3.pt --model_path=model/model_ver3_epoch_260.pth --query_dir=data/fma_large_5sec_2K --eval=True >> results/fma_large_5sec_2K.txt
# python test.py --fp_path=fingerprints/fma_large_ver3.pt --model_path=model/model_ver3_epoch_260.pth --query_dir=data/fma_large_6sec_2K --eval=True >> results/fma_large_6sec_2K.txt
# python test.py --fp_path=fingerprints/fma_large_ver5.pt --model_path=model/model_ver5_epoch_300.pth --query_dir=data/fma_large_10sec_5H --eval=True
# python main.py >> results/train_ver4.txt

