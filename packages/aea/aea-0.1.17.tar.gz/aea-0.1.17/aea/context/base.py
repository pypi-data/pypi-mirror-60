# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2019 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This module contains the agent context class."""

from queue import Queue
from typing import Any, Dict

from aea.connections.base import ConnectionStatus
from aea.crypto.ledger_apis import LedgerApis
from aea.decision_maker.base import GoalPursuitReadiness, OwnershipState, Preferences
from aea.mail.base import OutBox


class AgentContext:
    """Provide read access to relevant data of the agent for the skills."""

    def __init__(
        self,
        agent_name: str,
        public_keys: Dict[str, str],
        addresses: Dict[str, str],
        ledger_apis: LedgerApis,
        connection_status: ConnectionStatus,
        outbox: OutBox,
        decision_maker_message_queue: Queue,
        ownership_state: OwnershipState,
        preferences: Preferences,
        goal_pursuit_readiness: GoalPursuitReadiness,
        task_queue: Queue,
    ):
        """
        Initialize an agent context.

        :param agent_name: the agent's name
        :param public_keys: the public keys of the agent
        :param ledger_apis: the ledger apis
        :param connection_status: the connection status
        :param outbox: the outbox
        :param decision_maker_message_queue: the (in) queue of the decision maker
        :param ownership_state: the ownership state of the agent
        :param preferences: the preferences of the agent
        :param goal_pursuit_readiness: ready to pursuit its goals
        :param task_queue: the queue for the task to be processed enqueued by the agent.
        """
        self._shared_state = {}  # type: Dict[str, Any]
        self._agent_name = agent_name
        self._public_keys = public_keys
        self._addresses = addresses
        self._ledger_apis = ledger_apis
        self._connection_status = connection_status
        self._outbox = outbox
        self._decision_maker_message_queue = decision_maker_message_queue
        self._ownership_state = ownership_state
        self._preferences = preferences
        self._goal_pursuit_readiness = goal_pursuit_readiness
        self._task_queue = task_queue

    @property
    def shared_state(self) -> Dict[str, Any]:
        """Get the shared state dictionary."""
        return self._shared_state

    @property
    def agent_name(self) -> str:
        """Get agent name."""
        return self._agent_name

    @property
    def public_keys(self) -> Dict[str, str]:
        """Get public keys."""
        return self._public_keys

    @property
    def addresses(self) -> Dict[str, str]:
        """Get addresses."""
        return self._addresses

    @property
    def address(self) -> str:
        """Get the defualt address."""
        return self._addresses[self.ledger_apis.default_ledger_id]

    @property
    def public_key(self) -> str:
        """Get the default public key."""
        return self._public_keys[self.ledger_apis.default_ledger_id]

    @property
    def connection_status(self) -> ConnectionStatus:
        """Get connection status."""
        return self._connection_status

    @property
    def outbox(self) -> OutBox:
        """Get outbox."""
        return self._outbox

    @property
    def decision_maker_message_queue(self) -> Queue:
        """Get decision maker queue."""
        return self._decision_maker_message_queue

    @property
    def ownership_state(self) -> OwnershipState:
        """Get the ownership state of the agent."""
        return self._ownership_state

    @property
    def preferences(self) -> Preferences:
        """Get the preferences of the agent."""
        return self._preferences

    @property
    def goal_pursuit_readiness(self) -> GoalPursuitReadiness:
        """Get the goal pursuit readiness."""
        return self._goal_pursuit_readiness

    @property
    def ledger_apis(self) -> LedgerApis:
        """Get the ledger APIs."""
        return self._ledger_apis

    @property
    def task_queue(self) -> Queue:
        """Get the task queue."""
        return self._task_queue
