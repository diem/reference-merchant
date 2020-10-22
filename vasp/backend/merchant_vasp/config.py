import logging
import os

import dramatiq
import redis
from dramatiq.brokers.redis import RedisBroker, Broker
from dramatiq.encoder import PickleEncoder
from dramatiq.results import Results
from dramatiq.results.backends.redis import RedisBackend
from libra import testnet, identifier

DB_URL: str = os.getenv("DB_URL", "sqlite:////tmp/merchant_test.db")

PAYMENT_EXPIRE_MINUTES = 10

REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")


def calculate_chain_hrp() -> str:
    testnet_id = testnet.CHAIN_ID.value
    chain_id = int(os.getenv("CHAIN_ID", testnet_id))

    if chain_id == testnet_id:
        hdr = identifier.TLB
    else:
        hdr = identifier.LBR

    logging.warning(f"CHAIN: ID={chain_id} HDR={hdr}")
    return hdr


CHAIN_HRP: str = calculate_chain_hrp()


# init redis and dramatiq broker
def setup_redis_broker() -> None:
    _connection_pool: redis.BlockingConnectionPool = redis.BlockingConnectionPool(
        host=REDIS_HOST, port=REDIS_PORT, db=0, password=REDIS_PASSWORD
    )
    _redis_db: redis.StrictRedis = redis.StrictRedis(connection_pool=_connection_pool)
    _result_backend = RedisBackend(encoder=PickleEncoder(), client=_redis_db)
    _result_middleware = Results(backend=_result_backend)
    broker: Broker = RedisBroker(
        connection_pool=_connection_pool,
        middleware=[_result_middleware],
        namespace="lrm",
    )
    dramatiq.set_broker(broker)
    dramatiq.set_encoder(dramatiq.PickleEncoder())


if dramatiq.broker.global_broker is None:
    setup_redis_broker()
