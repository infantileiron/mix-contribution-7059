from enum import Enum
class Role(str,Enum):
 admin="admin"
 analyst="analyst"
 viewer="viewer"
class RunStatus(str,Enum):
 queued="queued"
 running="running"
 completed="completed"
 failed="failed"
class Factor(str,Enum):
 scale="scale"
 structure="structure"
 intensity="intensity"
