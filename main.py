from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import webbrowser

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, IBMQ
# from qiskit_ibm_provider import IBMQ
from qiskit.compiler import transpile
from qiskit.providers import JobError
from numpy import pi

backend_name = "ibmq_qasm_simulator"
tag          = "Quantum_dice_roller"

def states4():
    qreg_q = QuantumRegister(2, 'q')
    creg_c = ClassicalRegister(2, 'c')
    circuit = QuantumCircuit(qreg_q, creg_c)
    
    circuit.h(qreg_q[0])
    circuit.h(qreg_q[1])
    circuit.measure(qreg_q, creg_c)

    return circuit

def states6():
    qreg_q = QuantumRegister(3, 'q')
    creg_c = ClassicalRegister(3, 'c')
    circuit = QuantumCircuit(qreg_q, creg_c)

    circuit.h(qreg_q[0])
    circuit.rx(pi/1.644267775, qreg_q[2])
    circuit.ccx(qreg_q[0], qreg_q[2], qreg_q[1])
    circuit.rx(pi/2, qreg_q[0])
    circuit.x(qreg_q[2])
    circuit.measure(qreg_q, creg_c)

    return circuit

def states8():
    qreg_q = QuantumRegister(3, 'q')
    creg_c = ClassicalRegister(3, 'c')
    circuit = QuantumCircuit(qreg_q, creg_c)
    
    circuit.h(qreg_q[0])
    circuit.h(qreg_q[1])
    circuit.h(qreg_q[2])
    circuit.measure(qreg_q, creg_c)

    return circuit

def states10():
    qreg_q = QuantumRegister(4, 'q')
    creg_c = ClassicalRegister(4, 'c')
    circuit = QuantumCircuit(qreg_q, creg_c)
    
    circuit.h(qreg_q[0])
    circuit.h(  qreg_q[1])
    circuit.ry(pi / 1.41877626883, qreg_q[3])
    circuit.ccx(qreg_q[1], qreg_q[3], qreg_q[2])
    circuit.h(qreg_q[1])
    circuit.x(qreg_q[3])
    circuit.measure(qreg_q, creg_c)

    return circuit

def states12():    
    qreg_q = QuantumRegister(4, 'q')
    creg_c = ClassicalRegister(4, 'c')
    circuit = QuantumCircuit(qreg_q, creg_c)

    circuit.h(qreg_q[0])
    circuit.h(qreg_q[1])
    circuit.rx(pi / 1.644267775, qreg_q[3])
    circuit.ccx(qreg_q[0], qreg_q[3], qreg_q[2])
    circuit.rx(pi / 2, qreg_q[0])
    circuit.x(qreg_q[3])
    circuit.measure(qreg_q, creg_c)

    return circuit

def states20():    
    qreg_q = QuantumRegister(5, 'q')
    creg_c = ClassicalRegister(5, 'c')
    circuit = QuantumCircuit(qreg_q, creg_c)

    circuit.h(qreg_q[2])
    circuit.ry(pi / 1.41877626883, qreg_q[4])
    circuit.h(qreg_q[1])
    circuit.h(qreg_q[0])
    circuit.ccx(qreg_q[2], qreg_q[4], qreg_q[3])
    circuit.h(qreg_q[2])
    circuit.x(qreg_q[4])
    circuit.measure(qreg_q, creg_c)

    return circuit

# CNSTANT CIRCUITS
# create circuit for 4 states
circuit_4 = states4()
# create circuit for 6 states
circuit_6 = states6()
# create circuit for 8 states
circuit_8 = states8()
# create circuit for 10 states
circuit_10 = states10()
# create circuit for 12 states
circuit_12 = states12()
# create circuit for 20 states
circuit_20 = states20()

all_dices    = {
    'd4': circuit_4, 
    'd6': circuit_6, 
    'd8': circuit_8, 
    'd10': circuit_10, 
    'd12': circuit_12, 
    'd20': circuit_20
    }

class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/dice/f':
            # receive the request
            content_length = int(self.headers['Content-Length'])
            request_body = self.rfile.read(content_length)
            json_data = json.loads(request_body.decode('utf-8'))

            # Here, you can do whatever you need to do with the JSON data.
            # For example, you could process the data and send back a response.

            # print(json_data)

            # type of dice
            dice = json_data['data']
            print(dice)

            provider = IBMQ.get_provider(group='open')
            backend = provider.get_backend(backend_name)
            # n_qubits = backend.configuration().to_dict()["n_qubits"]

            jobs  = []
            count = 0
            # dice_shots = {'d4': 0, 'd6': 0, 'd8': 0, 'd10': 0, 'd12': 0, 'd20': 0}
            dice_shots = {}
            
            for d in dice:
                if d not in dice_shots:
                    dice_shots[d] = 1
                else:
                    dice_shots[d] += 1
            # print(dice_shots)
            
            job_id_d8 = ''
            for d in dice_shots.keys():
                transpiled_circuit = transpile(all_dices[d], backend)
                # print(transpiled_circuit.draw())
                try:
                    jobs.append(backend.run(transpiled_circuit, job_tags=[str(tag+'_'+d)], shots=dice_shots[d]))
                    count += 1
                    if d == 'd10':
                        job_id_d8 = jobs[-1].job_id()
                except Exception as e:
                    print("Error to run the job\n")
                    # sys.exit(0)

            if count > 0:
                queue_info = jobs[0].queue_info()
                if queue_info != None:
                    print(f"Remaining time is {queue_info.estimated_start_time.ctime()}")

            number = []
            for i in range(count):
                job_id = jobs[i].job_id()
                retrieved_job = backend.retrieve_job(job_id)

                try:
                    # It will block execution until the job finishes.
                    counts = retrieved_job.result().get_counts()
                    # number to extract from dices
                    if job_id_d8 == job_id:
                        for k in counts.keys():
                            result = int(k, 2)
                            for i in range(counts[k]):
                                number.append(result)
                    else:
                        for k in counts.keys():
                            result = int(k, 2)+1
                            for i in range(counts[k]):
                                number.append(result)

                except JobError as ex:
                    print("Error to run the job result\n")
                    # sys.exit(1)

            print(number)

            # send back the response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            dictionary = {'number': number}
            response_body = json.dumps(dictionary)
            self.wfile.write(response_body.encode('utf-8'))
    
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

if __name__ == '__main__':
    # Get the API token in
    # https://quantum-computing.ibm.com/

    with open('IBMQ_token.txt') as f:
        token = [line.rstrip() for line in f][0]

    print(token)
    IBMQ.save_account(token)
    IBMQ.load_account()

    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MyHTTPRequestHandler)
    print('Server running at http://localhost:8000')
    webbrowser.open("http://localhost:8000")

    httpd.serve_forever()