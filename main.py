import argparse
from src.logging import get_logger
get_logger()

from src.operators import *
from src.optimizer  import *
from src.quickbb_api import *
from cirq_test import *

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('circuitfile', help='file with circuit')
    parser.add_argument('target_state',
                        help='state x against which amplitude is computed')
    args = parser.parse_args()

    #target_amp = get_amplitude_from_cirq(
    #   args.circuitfile, args.target_state)

    n_qubits, circuit = read_circuit_file(args.circuitfile)

    graph , tensors = circ2graph(circuit)

    naive_eliminate(graph,tensors)
    cnffile = 'quickbb.cnf'
    gen_cnf(cnffile,graph)
    run_quickbb(cnffile)

if __name__=="__main__":
    log.info('h')
    main()