from typing import TypedDict, List, Literal

class ModelMessageConfig(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str

class ModelConfig(TypedDict):
    provider: str
    model: str
    messages: List[ModelMessageConfig]

class VoiceConfig(TypedDict):
    model: str
    voiceId: str
    provider: str
    stability: float
    similarityBoost: float

class TranscriberConfig(TypedDict):
    language: str
    provider: str

class AgentConfig(TypedDict):
    name: str
    model: ModelConfig
    voice: VoiceConfig
    transcriber: TranscriberConfig
    firstMessage: str
    serverMessages: List[str]
    silenceTimeoutSeconds: int
    maxDurationSeconds: int