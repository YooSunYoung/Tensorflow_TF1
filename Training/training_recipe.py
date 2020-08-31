def set_settings(flags):
    flags.DEFINE_boolean('validate', False, 'validation process included or not')
    flags.DEFINE_string('dataset', 'data/PolypImages_aug/', 'path to dataset')
    flags.DEFINE_string('val_dataset', 'data/PolypImages_valid/', 'path to validation dataset')
    flags.DEFINE_string('checkpoint_dir_path', 'results/checkpoints', 'path to checkpoint directory')
    flags.DEFINE_string('log_dir_path', 'results/logs/', 'path to log directory')
    flags.DEFINE_string('classes', 'data/polyp.names', 'path to classes file')
#   flags.DEFINE_string('device', '/GPU:0', 'name of the device for training')
    flags.DEFINE_integer('epochs', 500, 'number of epochs')
    flags.DEFINE_integer('save_point', 100, 'save weights every')
    flags.DEFINE_integer('validation_point', 30, 'save weights every')
    flags.DEFINE_integer('batch_size', 4, 'batch size')
    flags.DEFINE_integer('val_batch_size', 4, 'validation batch size')
    flags.DEFINE_float('learning_rate', 1e-3, 'learning rate')
