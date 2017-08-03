WinEvnt_Looker 
------------------------
    
    What is WinEvnt_Looker? Other than the crappy name, it is a Windows Event Log parser that stores data into Elasticsearch
    mapping. It is currently in its early stages of development. 
    New project name needed. WinEvnt_Looker sucks!
    
    
    *ISSUE 01: This will only work on Security.evtx file


Windows Events w/ elasticsearch mapping (json)
-----------------------------------------------
<pre>
[
    "mappings": { 
        "properties": { 
            "Event": {
                "System": {
                    "Guid": {"type": "string"},
                    "EventID": {"type": "string"},
                    "Version": {"type": "string"},
                    "Level" : {"type": "string"},
                    "Task": {"type": "string"},
                    "OpCode": {"type": "string"},
                    "Keywords": {"type": "string"},
                    "TimeCreate": {"type": "date"},
                    "EventRecordID": {"type": "string"},
                    "ProcessID": {"type": "string"},
                    "ThreadID": {"type": "string"},
                    "Channel": {"type": "string"},
                    "Computer": {"type": "string"},
                    "UserID": {"type": "string"}
                }
                "EventData": {
                    "SubjectUserSid": {"type": "string"},
                    ...
                    "This section will vary based on the Event ID."
                    "This section will be created dynamically."
                    ...
                    "n": {"type": "string"}
                }
            }
        }
    }
]
</pre>

License
-------------
"WinEvent_Looker" is licensed under the Apache License, Version 2.0. This means it is freely available for use and modification in a personal and professional capacity.