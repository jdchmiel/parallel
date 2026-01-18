export HIP_VISIBLE_DEVICES=0
/AI/llama.cpp/build/bin/llama-server -m /AI/models/qwen3/Qwen3-4B-Instruct-2507-UD-Q4_K_XL.gguf \
-c 64000 \
-ctk q8_0 \
-ctv q8_0 \
-ngl 99 \
--min-p 0 \
--top-k 20 \
--top-p 0.8 \
--temp 0.7 \
--host 0.0.0.0 \
--port 8080 \
-fa 1 \
-np 256

#177
