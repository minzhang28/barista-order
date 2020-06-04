from util.db import DBUtil
import falcon
import logging
import config
import json
from redis.exceptions import (
    ConnectionError,
    TimeoutError
)

logger = logging.getLogger(__name__)


class Register(object):
    def __init__(self, redis_conn):
        self.redis = redis_conn

    # TODO: Add schema validator here
    def on_post(self, req, resp):
        logger.info(req)
        store_name = req.media["store_name"]
        logger.info("creating record {}".format(req.media))
        try:
            if self.redis.hmset("store:{}".format(store_name), req.media) and self.redis.sadd("stores", store_name):
                resp.status = falcon.HTTP_201
                logger.info("store {} registered".format(store_name))
            else:
                logger.info("failed to register store")
                resp.status = falcon.HTTP_400
        except (TimeoutError, ConnectionError) as e:
            logger.error("failed to register store {} due to {}".format(store_name, e.msg))
            resp.status = falcon.HTTP_500

    def on_get(self, req, resp):
        try:
            keys = self.redis.smembers("stores")
            logger.debug("getting store list".format(keys))
            pipe = self.redis.pipeline()
            for key in keys:
                pipe.hgetall("store:{}".format(key))
            values = pipe.execute()
            logger.debug("successfully get all stores: {}".format(values))
            resp.body = json.dumps(values, sort_keys=True)
        except (TimeoutError, ConnectionError) as e:
            logger.error("failed to get stores from due to {}".format(e.msg))
            resp.status = falcon.HTTP_500
