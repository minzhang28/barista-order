from util.db import DBUtil
import falcon
import logging
import config
import json
from redis.exceptions import (
    ConnectionError,
    TimeoutError
)

from datetime import datetime

logger = logging.getLogger(__name__)


class Order(object):
    def __init__(self, redis_conn):
        self.redis = redis_conn

    def on_post(self, req, resp):
        """
        API to create orders. This API creates a few data objects as below
        1. add order details to users:orders:${username} HSET
        2. add item to store order history stores:order-histories:${store-name}
        """
        logger.info(req)
        username = req.media["username"]
        store_name = req.media["store_name"]
        orders = req.media["orders"]
        order_time = datetime.timestamp(datetime.now())
        pickup_time = float(req.media["pickup_time"])

        logger.info("creating record {}".format(req.media))
        try:
            pipe = self.redis.pipeline()
            # add order details to users:orders:${username} HSET
            pipe.hset("user:orders:{}".format(username), order_time, req.media)
            for order_item in orders.keys():
                pipe.zadd("stores:order:histories:{}".format(store_name), float(pickup_time), order_item)

            pipe.execute()
            resp.status = falcon.HTTP_201
            logger.info("order to {} created".format(store_name))

        except Exception as e:
            logger.error("failed to create order {} due to {}".format(store_name, e.msg))
            resp.status = falcon.HTTP_500

    def on_get(self, req, resp):
        try:
            store_name = req.params["store"]
            res = self.redis.zrange("stores:order:histories:{}".format(store_name), 0, -1, withscores=True)
            logger.debug("successfully get orders for store  {}".format(store_name))
            resp.body = json.dumps(res, sort_keys=True)
        except (TimeoutError, ConnectionError) as e:
            logger.error("failed to get stores from due to {}".format(e.msg))
            resp.status = falcon.HTTP_500
