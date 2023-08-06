import tensorflow as tf
import numpy

class Edge_Toolkit:

    def __init__(self, logging):
        self.logger = logging
        self.samples = None
        pass

    def convert_model_lite(self, calibration_data, model_name="model", tf_model_dir=None, keras_model=None):
        self.samples = calibration_data

        if tf_model_dir is not None:
            converter = tf.lite.TFLiteConverter.from_saved_model(tf_model_dir)
        else:
            keras_model.save("../storage/" + model_name + "." + constants.MODEL_EXTENSION)
            converter = tf.lite.TFLiteConverter.from_keras_model_file("../storage/" + model_name + "." + constants.MODEL_EXTENSION)

        converter.representative_dataset = self.representative_dataset_gen
        converter.optimizations = [tf.lite.Optimize.DEFAULT]

        try:
            tflite_model = converter.convert()
        except Exception as e:
            self.logger.error("Error converting model to tf lite: " + str(e))
            return False

        if tf_model_dir is not None:
            open('../storage/' + tf_model_dir + "/" + model_name + "." + constants.TF_LITE_EXTENSION, "wb").write(
                tflite_model)
            self.logger.info("Converted tf model " + str(tf_model_dir) + " to tf lite")
        else:
            open('../storage/' + model_name + "." + constants.TF_LITE_EXTENSION, "wb").write(
                tflite_model)
            self.logger.info("Converted keras model " + model_name + " to tf lite")
        
        return True

    def convert_model_tpu(self, calibration_data, model_name="model", tf_model_dir=None, keras_model=None)
        self.samples = calibration_data

        if tf_model_dir is not None:
            converter = tf.lite.TFLiteConverter.from_saved_model(tf_model_dir)
        else:
            keras_model.save("../storage/" + model_name + "." + constants.MODEL_EXTENSION)
            converter = tf.lite.TFLiteConverter.from_keras_model_file("../storage/" + model_name + "." + constants.MODEL_EXTENSION)

        converter.target_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
        converter.representative_dataset = self.representative_dataset_gen
        converter.inference_input_type = tf.uint8
        converter.inference_output_type = tf.uint8
        converter.optimizations = [tf.lite.Optimize.DEFAULT]

        try:
            tflite_model = converter.convert()
        except Exception as e:
            self.logger.error("Error converting model to tf lite: " + str(e))
            return

        if tf_model_dir is not None:
            open('../storage/' + tf_model_dir + "/" + model_name + constants.TF_LITE_EXTENSION, "wb").write(
                tflite_model)
            self.logger.info("Converted tf model " + str(tf_model_dir) + " to tf lite specific for TPU")

            cmd = ['edgetpu_compiler',
                "../storage/" + tf_model_dir + "/" + model_name + constants.TF_LITE_EXTENSION, '-o', args['output']]
        else:
            open('../storage/' + model_name + constants.TF_LITE_EXTENSION, "wb").write(
                tflite_model)
            self.logger.info("Converted keras model " + model_name + " to tf lite specific for TPU")

            cmd = ['edgetpu_compiler', '-o', '../storage',
                "../storage/" +  model_name + constants.TFLITE_EXTENSION]
         
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE)
        except FileNotFoundError as e:
            self.logger.error('The edge tpu complier is not installed: ' + str(e))
            return False
        except Exception as e:
            self.logger.error('The edge tpu complier throwed an error: ' + str(e))
            return False

        return True

    def representative_dataset_gen(self):
        for i in range(len(self.samples)):
            data = numpy.array(self.samples[i: i + 1], dtype=numpy.float32)
            yield [data]
