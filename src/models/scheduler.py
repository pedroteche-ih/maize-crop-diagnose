import tensorflow as tf
from tensorflow import keras

K = keras.backend


class OneCycleSchedulerNoMom(tf.keras.callbacks.Callback):
    def __init__(
        self,
        iterations,
        max_lr=1e-3,
        start_lr=None,
        last_iterations=None,
        last_lr=None,
    ):
        self.iterations = iterations
        self.max_lr = max_lr
        self.start_lr = start_lr or max_lr / 10
        self.last_iterations = last_iterations or iterations // 10 + 1
        self.half_iteration = (iterations - self.last_iterations) // 2
        self.last_lr = last_lr or self.start_lr / 1000
        self.iteration = 0

    def _interpolate(self, iter1, iter2, lr1, lr2):
        return (lr2 - lr1) * (self.iteration - iter1) / (iter2 - iter1) + lr1

    def on_batch_begin(self, batch, logs):
        if self.iteration < self.half_iteration:
            lr = self._interpolate(0, self.half_iteration, self.start_lr, self.max_lr)
        elif self.iteration < 2 * self.half_iteration:
            lr = self._interpolate(
                self.half_iteration, 2 * self.half_iteration, self.max_lr, self.start_lr
            )
        else:
            lr = self._interpolate(
                2 * self.half_iteration, self.iterations, self.start_lr, self.last_lr
            )
        self.iteration += 1
        K.set_value(self.model.optimizer.learning_rate, lr)
