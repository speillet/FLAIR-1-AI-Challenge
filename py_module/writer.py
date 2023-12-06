import os
from pickletools import uint8
import numpy as np
from pathlib import Path
from pytorch_lightning.callbacks import BasePredictionWriter
from pytorch_lightning.utilities.rank_zero import rank_zero_only 
from PIL import Image


class PredictionWriter(BasePredictionWriter):

    def __init__(
        self,
        output_dir,
        write_interval,
    ):
        super().__init__(write_interval)
        self.output_dir = output_dir
        Path(self.output_dir).mkdir(exist_ok=True, parents=True)

    def write_on_batch_end(
        self,
        trainer,
        pl_module,
        prediction,
        batch_indices,
        batch,
        batch_idx,
        dataloader_idx,
    ):
        preds, filenames = prediction["preds"], prediction["id"]
        preds = preds.cpu().numpy().astype('uint8')  # Pass prediction on CPU
        
        for prediction, filename in zip(preds, filenames):
            output_file = str(self.output_dir+'/'+filename.split('/')[-1].replace('IMG', 'PRED'))
            Image.fromarray(prediction).save(output_file,  compression='tiff_lzw')

    def on_predict_batch_end(
            self, 
            trainer, 
            pl_module, 
            outputs, 
            batch, 
            batch_idx, 
            dataloader_idx = 0):
        if not self.interval.on_batch:
            return

        batch_indices = trainer.predict_loop.current_batch_indices
        self.write_on_batch_end(
            trainer, pl_module, outputs, batch_indices, batch, batch_idx, dataloader_idx
        )
