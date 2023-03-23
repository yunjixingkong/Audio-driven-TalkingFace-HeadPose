from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks


models = {
    "aibei": "damo/speech_sambert-hifigan_tts_zhibei_emo_zh-cn_16k",
    "aitian": "damo/speech_sambert-hifigan_tts_zhitian_emo_zh-cn_16k",
    "aiyan": "damo/speech_sambert-hifigan_tts_zhiyan_emo_zh-cn_16k",
    "aizhe": "damo/speech_sambert-hifigan_tts_zhizhe_emo_zh-cn_16k"
}

class ModelScopeTTS():
    def __init__(self) -> None:
        self.models = {
            "aibei": pipeline(task=Tasks.text_to_speech, model="damo/speech_sambert-hifigan_tts_zhibei_emo_zh-cn_16k"),
            "aitian": pipeline(task=Tasks.text_to_speech, model="damo/speech_sambert-hifigan_tts_zhitian_emo_zh-cn_16k"),
            "aiyan": pipeline(task=Tasks.text_to_speech, model="damo/speech_sambert-hifigan_tts_zhiyan_emo_zh-cn_16k"),
            "aizhe": pipeline(task=Tasks.text_to_speech, model="damo/speech_sambert-hifigan_tts_zhizhe_emo_zh-cn_16k"),
        }

    def infer(self, timbre, text, output):
        model = self.models[timbre]
        data = model(input=text)
        wav = data[OutputKeys.OUTPUT_WAV]
        with open(output, 'wb') as f:
            f.write(wav)

