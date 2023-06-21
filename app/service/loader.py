import gensim
import torch
import underthesea
import numpy as np
from typing import List
from transformers import (
    AutoModel,
    AutoTokenizer,
    T5ForConditionalGeneration,
    T5Tokenizer,
)
from sklearn.preprocessing import MultiLabelBinarizer

from app.core.config import project_config
from app.worker.socket import SocketPayload, socket_worker
from app.util.time import get_current_timestamp


class Loader:
    def __init__(self) -> None:
        if torch.cuda.is_available():
            self.__device = torch.device("cuda")

            print("There are %d GPU(s) available." % torch.cuda.device_count())

            print("We will use the GPU:", torch.cuda.get_device_name(0))
        else:
            print("No GPU available, using the CPU instead.")
            self.__device = torch.device("cpu")

        # Load model vector hóa
        self.__phobert = AutoModel.from_pretrained("vinai/phobert-base").to(
            self.__device
        )
        self.__tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")

        # # Load model summarization
        # self.model = T5ForConditionalGeneration.from_pretrained("NlpHUST/t5-small-vi-summarization").to(device)
        # self.t5tokenizer = T5Tokenizer.from_pretrained("NlpHUST/t5-small-vi-summarization")

        self.__stop_word_data = np.genfromtxt(
            project_config.STOPWORD_PATH, dtype="str", delimiter="\n", encoding="utf8"
        ).tolist()

    async def feature_engineering(self, data: List, client_id: str = None):
        features_set = []
        for line_idx, line in enumerate(data):
            line = gensim.utils.simple_preprocess(str(line))  # Tiền xử lý dữ liệu
            line = " ".join(line)
            line = underthesea.word_tokenize(line, format="text")  # Segment word
            line = " ".join(
                [word for word in line.split() if word not in self.__stop_word_data]
            )
            # if len(line.split()) > 100: # Summary long text
            # self.model.eval()
            #   tokenized_text = self.t5tokenizer.encode(line, return_tensors="pt").to(self.__device)
            #   summary_ids = model.generate(
            #                       tokenized_text,
            #                       max_length=256,
            #                       num_beams=5,
            #                       repetition_penalty=2.5,
            #                       length_penalty=1.0,
            #                       early_stopping=True
            #                   )
            #   line = self.t5tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            line = self.__tokenizer(line, truncation=True).input_ids  # tokenizer
            input_ids = torch.tensor([line]).to(torch.long)
            with torch.no_grad():  # Lấy features dầu ra từ BERT
                features = self.__phobert(input_ids)
            v_features = features[0][:, 0, :].numpy()
            features_set.append(v_features[0])
            if client_id:
                socket_worker.push(
                    SocketPayload(
                        data={
                            "time": get_current_timestamp(),
                            "content": f"Dữ liệu văn bản số {line_idx}",
                        },
                        channel="deployLog",
                        client_id=client_id,
                    )
                )
        features_set = np.array(features_set)
        return features_set

    async def multilabel_binarizing(self, raw_data, classes, client_id: str = None):
        multilabel_binarizer = MultiLabelBinarizer(classes=classes, sparse_output=True)
        data = [i if isinstance(i, list) else [i] for i in raw_data]
        return multilabel_binarizer.fit_transform(data).toarray()

    async def numerical_vectorize(slef, raw_data, client_id: str = None):
        res = []
        for data in raw_data:
            try:
                res.append([float(data)])
            except:
                res.append([0])
        return res


loader = Loader()
