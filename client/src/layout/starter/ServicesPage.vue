<script setup>
import { selectedVm } from "../../main.js";
</script>

<template>

  <div class="container">

    <div class="mobile-nav-bar__buttons">
    <template v-if="!$auth0.isAuthenticated">
      <SignupButton />
      <LoginButton />
    </template>
    <template v-if="$auth0.isAuthenticated">
    </template>
  </div>

    <div class="row">
      <div class="col-sm-10">
        <h1>Available Services</h1>
        <hr />

        <ul v-if="vms && vms.length > 0">

        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">Image name</th>
              <th scope="col">Services</th>
              <th scope="col">Volumes</th>
              <th scope="col">Enviroment Variables</th>
            </tr>

          </thead>

          <tbody>
              <tr v-for="(vm, index) in vms" :key="vm.image">
                
                <td>{{ vm.image }}</td>
                <td>
                <table class="table table-hover" style=" background: transparent" >
                    <thead>
                        <tr>
                        <th scope="col">service name</th>
                        <th scope="col">service port</th>
                        <th scope="col">container port</th>
                        <th scope="col">priority</th>

                        <th></th>
                        </tr>

                    </thead>

                    <tbody> 
                         <tr v-for="(service, index) in vm.services" :key="service.port"  class="nested-table">
                            <td>{{ service.name }}</td>
                            <td>{{ service.service_port }}</td>
                            <td>{{ service.container_port }}</td>
                            <td>
                              
                              <div style="display: flex; gap: 5px; align-items: center">
                                {{ service.priority }} 

                              <button
                      type="button"
                      class="btn btn-warning btn-sm"
                      @click="(selectedVm.vmId = vm.name), toggleUpdateVmModal()"
                    >
                      Update
                    </button>
                  </div>

                            </td>

                         </tr>

                        
                        
                        
                    </tbody>

                    </table>
                </td>
              
                <td>
                    <div v-for="(volume, index) in vm.volumes" :key="volume.host"  class="nested-table">
                        {{ volume.host }} : {{ volume.container }}
                    </div>     
                          
                </td> 
                    
             

                
       
                
              


              </tr>
          </tbody>

        </table>

      </ul><p v-else>No VMs found.</p>

      </div>
    </div>

    <!-- add new vm modal -->
    <div
      ref="addVmModal"
      class="modal fade"
      :class="{ show: activeAddVmModal, 'd-block': activeAddVmModal }"
      tabindex="-1"
      role="dialog"
    >
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add a new VM</h5>
            <button
              type="button"
              class="close"
              data-dismiss="modal"
              aria-label="Close"
              @click="toggleAddVmModal"
            >
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <form>
              <div class="mb-3">
                <label for="addVMName" class="form-label">Name:</label>
                <input
                  type="text"
                  style="color: black"
                  class="form-control"
                  id="addVMName"
                  v-model="addVMForm.name"
                  placeholder="Enter name of the VM"
                />
              </div>
              <div class="mb-3">
                <label for="addVMCPU" class="form-label">CPUs:</label>
                <input
                  type="text"
                  style="color: black"
                  class="form-control"
                  id="addVMCPU"
                  v-model="addVMForm.cpus"
                  placeholder="Enter number of CPUs"
                />
              </div>
              <div class="mb-3">
                <label for="addVMRAM" class="form-label">RAM:</label>
                <input
                  type="text"
                  style="color: black"
                  class="form-control"
                  id="addVMRAM"
                  v-model="addVMForm.ram"
                  placeholder="Enter RAM (MB)"
                />
              </div>

              <div class="mb-3">
                <label for="addVMIP" class="form-label">IP:</label>
                <input
                  type="text"
                  style="color: black"
                  class="form-control"
                  id="addVMIP"
                  v-model="addVMForm.ip"
                  placeholder="Enter IP address"
                />
              </div>

              <div class="btn-group" role="group">
                <button
                  type="button"
                  class="btn btn-primary btn-sm"
                  @click="handleAddSubmit"
                >
                  Submit
                </button>
                <button
                  type="button"
                  class="btn btn-danger btn-sm"
                  @click="handleAddReset"
                >
                  Reset
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- update vm modal -->
    <div
      ref="updateVmModal"
      class="modal fade"
      :class="{ show: activeUpdateVmModal, 'd-block': activeUpdateVmModal }"
      tabindex="-1"
      role="dialog"
    >
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Update a new VM</h5>
            <button
              type="button"
              class="close"
              data-dismiss="modal"
              aria-label="Close"
              @click="(selectedVm.vmId = ''), toggleUpdateVmModal()"
            >
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <form>
              <div class="mb-3">
                <label for="updateVMCPU" class="form-label">CPUs:</label>
                <input
                  type="text"
                  style="color: black"
                  class="form-control"
                  id="updateVMCPU"
                  v-model="updateVMForm.cpus"
                  placeholder="Enter number of CPUs"
                />
              </div>
              <div class="mb-3">
                <label for="updateVMRAM" class="form-label">RAM:</label>
                <input
                  type="text"
                  style="color: black"
                  class="form-control"
                  id="updateVMRAM"
                  v-model="updateVMForm.ram"
                  placeholder="Enter RAM (MB)"
                />
              </div>

              <div class="mb-3">
                <label for="updateVMIP" class="form-label">IP:</label>
                <input
                  type="text"
                  style="color: black"
                  class="form-control"
                  id="updateVMIP"
                  v-model="updateVMForm.ip"
                  placeholder="Enter IP address"
                />
              </div>

              <div class="btn-group" role="group">
                <button
                  type="button"
                  class="btn btn-primary btn-sm"
                  @click="handleUpdateSubmit(selectedVm.vmId)"
                >
                  Submit
                </button>
                <button
                  type="button"
                  class="btn btn-danger btn-sm"
                  @click="handleUpdateReset"
                >
                  Reset
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    <div v-if="activeUpdateVmModal" class="modal-backdrop fade show"></div>
  </div>

  
</template>

<script>
import axios from "axios";


export default {
  data() {
    return {
      activeAddVmModal: false,
      activeUpdateVmModal: false,
      addVMForm: {
        name: "",
        cpus: "",
        ram: "",
        ip: "",
      },
      updateVMForm: {
        cpus: "",
        ram: "",
        ip: "",
      },
      vms: [],
    };
  },
  methods: {
    addVm(payload) {
      const path = "http://localhost:5000/vm/create";
      axios
        .post(path, payload)
        .then(() => {
          this.getVMs();
        })
        .catch((error) => {
          console.log(error);
          this.getVMs();
        });
    },
    updateVm(vmId, payload) {
      const path = `http://localhost:5000/vm/update/${vmId}`;
      axios
        .post(path, payload)
        .then(() => {
          this.getVMs();
        })
        .catch((error) => {
          console.log(error);
          this.getVMs();
        });
    },
    getVMs() {
      const path = "http://localhost:5000/services/list";
      axios
        .get(path)
        .then((res) => {
          this.vms = res.data;
          console.log(res.data)
        })
        .catch((error) => {
          console.error(error);
        });
    },
    handleAddReset() {
      this.initAddForm();
    },
    handleUpdateReset() {
      this.initUpdateForm();
    },
    handleAddSubmit() {
      this.toggleAddVmModal();
      // let read = false;
      // if (this.addVMForm.read[0]) {
      //   read = true;
      // }
      const payload = {
        name: this.addVMForm.name,
        cpus: this.addVMForm.cpus,
        ram: this.addVMForm.ram,
        ip: this.addVMForm.ip,
      };
      this.addVm(payload);
      this.initAddForm();
    },
    handleUpdateSubmit(vm) {
      this.toggleUpdateVmModal;
      // let read = false;
      // if (this.addVMForm.read[0]) {
      //   read = true;
      // }
      const payload = {
        cpus: this.updateVMForm.cpus,
        ram: this.updateVMForm.ram,
        ip: this.updateVMForm.ip,
      };
      console.log(vm);
      this.updateVm(vm, payload);
      this.initUpdateForm();
    },
    initAddForm() {
      this.addVMForm.name = "";
      this.addVMForm.cpus = "";
      this.addVMForm.ram = "";
      this.addVMForm.ip = "";
    },
    initUpdateForm() {
      this.updateVMForm.cpus = "";
      this.updateVMForm.ram = "";
      this.updateVMForm.ip = "";
    },
    toggleAddVmModal() {
      const body = document.querySelector("body");
      this.activeAddVmModal = !this.activeAddVmModal;
      if (this.activeAddVmModal) {
        body.classList.add("modal-open");
      } else {
        body.classList.remove("modal-open");
      }
    },
    toggleUpdateVmModal() {
      const body = document.querySelector("body");
      this.activeUpdateVmModal = !this.activeUpdateVmModal;
      if (this.activeUpdateVmModal) {
        body.classList.add("modal-open");
      } else {
        body.classList.remove("modal-open");
      }
    },

    handleDeleteVm(vm) {
      this.removeVm(vm.name);
    },
    removeVm(vmID) {
      const path = `http://localhost:5000/vm/delete/${vmID}`;
      axios
        .delete(path)
        .then(() => {
          //this.getVMs();
          this.message = "Vm removed!";
          this.showMessage = true;
        })
        .catch((error) => {
          console.error(error);
          //this.getVms();
        });
    },
    handleReloadVm(vm) {
      this.reloadVm(vm.name);
    },
    reloadVm(vmID) {
      const path = `http://localhost:5000/vm/reload/${vmID}`;
      axios
        .post(path)
        .then(() => {
          //this.getVMs();
          this.message = "Vm reloaded!";
          this.showMessage = true;
        })
        .catch((error) => {
          console.error(error);
          //this.getVms();
        });
    },
    handleStartVm(vm) {
      this.startVm(vm.name);
    },
    startVm(vmID) {
      const path = `http://localhost:5000/vm/start/${vmID}`;
      axios
        .post(path)
        .then(() => {
          this.getVMs();
          this.message = "Vm started!";
          this.showMessage = true;
        })
        .catch((error) => {
          console.error(error);
          this.getVms();
        });
    },
    handleStopVm(vm) {
      this.stopVm(vm.name);
    },
    stopVm(vmID) {
      const path = `http://localhost:5000/vm/stop/${vmID}`;
      axios
        .post(path)
        .then(() => {
          this.getVMs();
          this.message = "Vm stopped!";
          this.showMessage = true;
        })
        .catch((error) => {
          console.error(error);
          this.getVms();
        });
    },
  },
  created() {
    this.getVMs();
  },
};


</script>


