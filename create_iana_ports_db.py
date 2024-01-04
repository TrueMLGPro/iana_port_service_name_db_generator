import csv
import os
import sqlite3
import urllib
import urllib.request

print("[i] Script started")
url = "https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.csv"
iana_ports_db = "iana_ports.db"
local_iana_csv = "service-names-port-numbers.csv"
line_count = 0

def download_csv():
	with urllib.request.urlopen(url) as response, open(local_iana_csv, 'wb') as out_file:
		# Response data stored in bytes
		data = response.read()
		out_file.write(data)
		out_file.close()
		response.close()
	print("[!] Download finished!")

# Download service-names-port-numbers.csv if it doesn't exist locally or if local csv file is 0 bytes in size
if not os.path.exists(local_iana_csv):
	print(f"[!] {local_iana_csv} doesn't exist, downloading it!")
	download_csv()
else:
	if os.stat(local_iana_csv).st_size == 0:
		print(f"[!] {local_iana_csv} exists but is empty, downloading it!")
		os.remove(local_iana_csv)
		download_csv()
	print(f"[i] {local_iana_csv} exists, creating vendor database")

try:
	if os.path.exists(iana_ports_db):
		# Remove the old DB if it exists
		print(f"[i] Old {iana_ports_db} exists, removing it")
		os.remove(iana_ports_db)
		# Create a new file
		print(f"[i] Creating {iana_ports_db}")
		open(iana_ports_db, "a").close()
except OSError as err:
	print(err)

conn = sqlite3.connect(iana_ports_db)
cursor = conn.cursor()
print("[i] Creating database table 'ports'")
cursor.execute('''
	CREATE TABLE IF NOT EXISTS ports (
		name TEXT,
		number INTEGER,
		protocol TEXT,
		description TEXT
	)
''')

# Parse the CSV file
with open(local_iana_csv, 'r') as file:
	reader = csv.reader(file)

	# Skip the header row
	next(reader)

	# Iterate over each row and insert data into the database
	for row in reader:
		name = row[0]
		number_range = row[1]
		protocol = row[2]
		description = row[3]

		if len(name) == 0:
			name = "-"

		# Handle port ranges
		if '-' in number_range:
			start, end = number_range.split('-')
			start = int(start)
			end = int(end)

			for port in range(start, end + 1):
				line_count += 1
				print(f"[i] Inserting line {line_count} into table 'ports'")
				# Insert the data into the database
				cursor.execute('INSERT INTO ports VALUES (?, ?, ?, ?)', (name, port, protocol, description))
		elif number_range:
			line_count += 1
			print(f"[i] Inserting line {line_count} into table 'ports'")
			number = int(number_range)
			# Insert the data into the database
			cursor.execute('INSERT INTO ports VALUES (?, ?, ?, ?)', (name, number, protocol, description))

print("[i] Applying changes and closing the database file")
conn.commit()
conn.close()
print("[✓] Done!")
