# ResearchForge: Python app + DeepSeek Harness (Node.js) in one image.
FROM node:24-bookworm-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-venv python3-pip git ca-certificates \
 && rm -rf /var/lib/apt/lists/*

ARG DSH_VERSION=0.1.7-rc.2
RUN npm install -g "@deepseek-ai/dsh@${DSH_VERSION}"

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY dsh-bundle ./dsh-bundle
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir ".[pdf]"
ENV PATH="/opt/venv/bin:${PATH}" \
    RF_PROJECTS_DIR=/app/research_projects \
    RF_DSH_HOME=/app/dsh-home \
    RF_DSH_COMMAND=dsh

EXPOSE 8765
# The UI has no authentication; publish the port only to localhost (docker run -p 127.0.0.1:8765:8765).
CMD ["researchforge", "serve", "--host", "0.0.0.0", "--port", "8765"]
