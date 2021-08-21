#!/bin/sh
python test.py --test_dir=data/test_data/fma_large --model_path=model/model_ver3_epoch_300.pth
python create_query_data.py --length 2 5 10 --test_dir=data/test_data/fma_large --noise_dir=data/Noises_unsampled --ir_dir=data/ir_filters
python test.py --fp_path=fingerprints/fma_large_ver3.pt --model_path=model/model_ver3_epoch_300.pth --query_dir=data/fma_large_2sec_2K --eval=True >> results/fma_large_2sec_2K.txt
python test.py --fp_path=fingerprints/fma_large_ver3.pt --model_path=model/model_ver3_epoch_300.pth --query_dir=data/fma_large_5sec_2K --eval=True >> results/fma_large_5sec_2K.txt
python test.py --fp_path=fingerprints/fma_large_ver3.pt --model_path=model/model_ver3_epoch_300.pth --query_dir=data/fma_large_10sec_2K --eval=True >> results/fma_large_10sec_2K.txt

