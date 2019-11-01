import spell.client
client = spell.client.from_environment()
r = client.runs.new(command="sleep 20", machine_type="CPU")
r.wait_status(client.runs.RUNNING)
print(r.run.id)