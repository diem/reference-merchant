# Copyright (c) The Libra Core Contributors
# SPDX-License-Identifier: Apache-2.0

# keep config import first, because we MUST configure dramatiq broker prior to background_tasks import
# once @actor is being used (e.g. in background_tasks) and no global dramatiq broker configured -
# dramatiq will try to use default RabbitMQ one (this is hardcoded and can't be changed) - which will fail
from . import background_tasks
