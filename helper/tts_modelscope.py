from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks


models = {
    "zhiyan": "damo/speech_sambert-hifigan_tts_zhiyan_emo_zh-cn_16k",
    "zhitian": "damo/speech_sambert-hifigan_tts_zhitian_emo_zh-cn_16k",
}

class ModelScopeTTS():
    def __init__(self) -> None:
        self.models = {
            "zhiyan": pipeline(task=Tasks.text_to_speech, model="damo/speech_sambert-hifigan_tts_zhiyan_emo_zh-cn_16k"),
            "zhitian": pipeline(task=Tasks.text_to_speech, model="damo/speech_sambert-hifigan_tts_zhitian_emo_zh-cn_16k"),
        }

    def infer(self, timbre, text, output):
        model = self.models[timbre]
        data = model(input=text)
        wav = data[OutputKeys.OUTPUT_WAV]
        with open(output, 'wb') as f:
            f.write(wav)

