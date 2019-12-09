'''
print(sys.version)
api_1  | 3.6.9 |Anaconda, Inc.| (default, Jul 30 2019, 19:07:31) 
api_1  | [GCC 7.3.0]
'''
# standard library
from pathlib import Path
import io

# external library
import librosa
import torch
import numpy as np
import soundfile as sf

# project library
import common.wrapper as wrapper
import common.constants as constants

from encoder import inference as encoder
from synthesizer.inference import Synthesizer
from vocoder import inference as vocoder

# global
synthesizer = None

def tts(input_dict):
    '''
    Flow:
    0) Check if audio has embeddings (Not yet)
    1) Encode the audio
    2) Synthesizer the text with embeddings
    3) Vocoder out the fake wav
    '''
    # init
    output_dict = {
        "data": {}
    }

    # loop the input
    for audio_name, raw_audio in input_dict["data"].items():
        wav_name_no_ext = Path(audio_name).stem
        saved_path_obj = Path.cwd() / "data/output"

        # step 1
        print("Step 1")
        raw_audio_np, sample_rate = librosa.load(io.BytesIO(raw_audio))
        preprocessed_wav = encoder.preprocess_wav(raw_audio_np, sample_rate)
        embeddings = encoder.embed_utterance(preprocessed_wav)

        # step 2
        print("Step 2")
        splitted_text = input_dict["text"].split(".")
        clean_text_list = [text for text in splitted_text if len(text) > 0]
        if len(clean_text_list) == 0:
            raise Exception("Empty text field")
        sentence_count = len(clean_text_list)
        embeddings_list = [embeddings] * sentence_count
        specs = synthesizer.synthesize_spectrograms(clean_text_list, embeddings_list)

        # step 3
        print("Step 3")
        for index, spec in enumerate(specs):
            generated_wav = vocoder.infer_waveform(spec)
            # needed to 1 second for playback capability
            generated_wav = np.pad(generated_wav, (0, synthesizer.sample_rate), mode="constant")

            file_name = "{}_tts_{}.wav".format(wav_name_no_ext, index)
            file_path = saved_path_obj / file_name
            sf.write(str(file_path), generated_wav.astype(np.float32), synthesizer.sample_rate, 'PCM_16')
            output_dict["data"][index] = file_path

    return output_dict

if __name__ == "__main__":
    # check for cuda support
    if not torch.cuda.is_available():
        print("Your PyTorch installation is not configured to use CUDA. If you have a GPU ready "
              "for deep learning, ensure that the drivers are properly installed, and that your "
              "CUDA version matches your PyTorch installation. CPU-only inference is currently "
              "not supported.")
        raise Exception("No CUDA support in TTS!")

    # load the model
    model_path_obj = Path.cwd() / "model"
    encoder_model_path = model_path_obj / "encoder/saved_models/pretrained.pt"
    sythesizer_model_path = model_path_obj / "synthesizer/saved_models/logs-pretrained/taco_pretrained"
    vocoder_model_path = model_path_obj / "vocoder/saved_models/pretrained/pretrained.pt"

    encoder.load_model(encoder_model_path)
    synthesizer = Synthesizer(sythesizer_model_path, low_mem=False) # 6gb not enough
    vocoder.load_model(vocoder_model_path)

    print("Loaded all model")

    # init
    master_server_ip_addr = "master"
    component_name = constants.Component.TTS
    # run the component
    run_obj = wrapper.WorkerWrapper(tts, component_name, master_server_ip_addr)
    run_obj.run()