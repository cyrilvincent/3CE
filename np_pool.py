import config
import logging
from np_product_nearest import NPNearestNN


class NPNearestPool:

    def __init__(self):
        self.pool = {}
        for instance in config.pool: # TYPER LES POOLS (nn, images, ...)
            path = config.product_h_file.replace("{instance}", instance)
            self.pool[instance] = NPNearestNN(path, use2=True)

    def get_instance(self, instance: str):
        return self.get_instance_nn(instance).np

    def get_instance_nn(self, instance: str):
        if instance in self.pool:
            return self.pool[instance]
        else:
            msg = f"Instance {instance} does not exist"
            logging.error(msg)
            raise ValueError(msg)

    def __getitem__(self, item):
        return self.get_instance_nn(item)

    def reset(self):
        for k in self.pool.keys():
            self.pool[k].reset()

if __name__ == '__main__':
    pool = NPNearestPool()
    print(pool.pool)