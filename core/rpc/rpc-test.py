import urllib
import urllib2

url = 'http://127.0.0.1:8008/jsonrpc'
# values = '{"jsonrpc" : "2.0", "method" : "message", "params" : {"content":{"command":"inventory"}}, "id":1 }'
# values = '{"jsonrpc" : "2.0", "method" : "message", "params" : {"content":{"command":"off", "uuid":"0962f27e-99ce-43a4-872b-97d75d61f464"}}, "id":1 }'
# values = '{"method":"message","params":{"content":{"command":"inventory"}},"id":1,"jsonrpc":"2.0"}'
# values = '[{"method":"message","params":{"content":{"command":"inventory"}},"id":null,"jsonrpc":"2.0"}, {"jsonrpc" : "2.0", "method" : "message", "params" : {"content":{"command":"off", "uuid":"0962f27e-99ce-43a4-872b-97d75d61f464"}}, "id":2 },{"jsonrpc" : "2.0", "method" : "message", "params" : {"content":{"command":"off", "uuid":"0962f27e-99ce-43a4-872b-97d75d61f464"}}},{"jsonrpc" : "2.0", "method" : "message", "params" : {"content":{"command":"off", "uuid":"0962f27e-99ce-43a4-872b-97d75d61f464"}}, "id":4 },{"method":"message","params":{"content":{"command":"inventory"}},"jsonrpc":"2.0"}]'
values = '{"method":"message","params":{"content":{"command":"inventory"}},"id":1,"jsonrpc":"2.0"}'
#values = '{"method":"subscribe","id":1,"jsonrpc":"2.0"}'
# values = '{"method":"unsubscribe","params":{"uuid": "401ae021-aad3-431e-bff7-dc95549799b6"},"id":1,"jsonrpc":"2.0"}'
# values = '{"method":"getevent","params":{"uuid": "8ebb77e0-ad9a-4279-9d29-990af0f115c1"},"id":1,"jsonrpc":"2.0"}'
# values = '{"method":"unsubscribe","id":1,"jsonrpc":"2.0"}'
# req = urllib2.Request(url, values)
# response = urllib2.urlopen(req)
# print response.read()
values = '{"method":"message","params":{"content":{"command":"getscenario","uuid":"457991c4-4d3e-4533-82dc-2da65e4b6f27","scenario":"aee6193d-e331-4c81-85fa-aefa28d78939"}},"id":1,"jsonrpc":"2.0"}'
print values
req = urllib2.Request(url, values)
response = urllib2.urlopen(req)
print response.read()
values = '{"method":"message","params":{"content":{"command":"setscenario","uuid":"457991c4-4d3e-4533-82dc-2da65e4b6f27","scenariomap":{"1":{"command":"on","uuid":"c81a868e-e3da-418a-9f4e-fbfa30dfdcb9"},"2":{"command":"scenariosleep","delay":5},"3":{"command":"off","uuid":"c81a868e-e3da-418a-9f4e-fbfa30dfdcb9"}}}},"id":2,"jsonrpc":"2.0"}'
print values
req = urllib2.Request(url, values)
response = urllib2.urlopen(req)
print response.read()
values = '{"method":"message","params":{"content":{"command":"delscenario","uuid":"457991c4-4d3e-4533-82dc-2da65e4b6f27","scenario":"525f9432-2cf7-4482-a8a9-faa44d0cd117"}},"id":3,"jsonrpc":"2.0"}'
print values
req = urllib2.Request(url, values)
response = urllib2.urlopen(req)
print response.read()
