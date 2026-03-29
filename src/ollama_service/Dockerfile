FROM ollama/ollama:latest

# Start the server in the background, wait for it to wake up, pull the model, and shut down cleanly
RUN ollama serve & \
    serve_pid=$! && \
    echo "Waiting for Ollama server..." && \
    while ! ollama list > /dev/null 2>&1; do sleep 1; done && \
    echo "Pulling qwen3.5:2b..." && \
    ollama pull qwen3.5:2b && \
    echo "Model pulled! Shutting down server to save image layer..." && \
    kill $serve_pid && \
    wait $serve_pid 2>/dev/null || true