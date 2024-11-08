<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Virtual Machines</h1>
        <hr><br><br>
        <button
        type="button"
        class="btn btn-success btn-sm"
        @click="toggleAddVmModal">
        Add VM
        </button>
        <br><br>
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">Name</th>
              <th scope="col">Status</th>
              <th scope="col">Action</th>
              <th scope="col">Containers</th>
              <th></th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="(vm, index) in vms" :key="index">
              <td>{{ vm.name}}</td>
              <td>{{ vm.status}}</td>
              
              
              <td>
                <div class="btn-group" role="group">
                  <button type="button" class="btn btn-warning btn-sm">Update</button>
                  <button
                    type="button"
                    class="btn btn-danger btn-sm"
                    @click="handleDeleteVm(vm)">
                    Delete
                  </button>
                </div>
              </td>
              
              <!-- Placeholder for Container Info-->
              <td>

                <button
                  type="button"
                  class="btn btn-success btn-sm"
                  @click="toggleAddContainerModal">
                  Add Container
                </button>

                <br><br>

                <tr v-for="(vm, index) in vms" :key="index">
                <td>{{ vm.name}}</td>
                <td>
                <div class="btn-group" role="group">
                  <button type="button" class="btn btn-warning btn-sm">Update</button>
                  <button
                    type="button"
                    class="btn btn-danger btn-sm"
                    @click="handleDeleteVm(vm)">
                    Delete
                  </button>
                </div>
              </td>
                </tr>
              </td>
            </tr>

            

          </tbody>
        </table>
      </div>
    </div>

<!-- add new vm modal -->
<div
ref="addVmModal"
class="modal fade"
:class="{ show: activeAddVmModal, 'd-block': activeAddVmModal }"
tabindex="-1"
role="dialog">
<div class="modal-dialog" role="document">
  <div class="modal-content">
    <div class="modal-header">
      <h5 class="modal-title">Add a new VM</h5>
      <button
        type="button"
        class="close"
        data-dismiss="modal"
        aria-label="Close"
        @click="toggleAddVmModal">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
    <div class="modal-body">
      <form>
        <div class="mb-3">
          <label for="addVMName" class="form-label">Name:</label>
          <input
            type="text"
            class="form-control"
            id="addVMName"
            v-model="addVMForm.name"
            placeholder="Enter name of the VM">
        </div>
        <div class="mb-3">
          <label for="addVMCPU" class="form-label">CPUs:</label>
          <input
            type="text"
            class="form-control"
            id="addVMCPU"
            v-model="addVMForm.cpu"
            placeholder="Enter number of CPUs">
        </div>
        <div class="mb-3">
          <label for="addVMRAM" class="form-label">RAM:</label>
          <input
            type="text"
            class="form-control"
            id="addVMRAM"
            v-model="addVMForm.ram"
            placeholder="Enter RAM (MB)">
        </div>
        
        <div class="btn-group" role="group">
          <button
            type="button"
            class="btn btn-primary btn-sm"
            @click="handleAddSubmit">
            Submit
          </button>
          <button
            type="button"
            class="btn btn-danger btn-sm"
            @click="handleAddReset">
            Reset
          </button>
        </div>
      </form>
    </div>
  </div>
</div>
</div>
<div v-if="activeAddVmModal" class="modal-backdrop fade show"></div>

  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      activeAddVmModal: false,
      addVMForm: {
        name: '',
        cpu: '',
        ram: '',
      },
      vms: [],
    };
  },
  methods: {
    
    addVm(payload) {
      const path = 'http://localhost:5000/create';
      axios.post(path, payload)
        .then(() => {
          this.getVMs();
        })
        .catch((error) => {

          console.log(error);
          this.getVMs();
        });
    },
    getVMs() {
      const path = 'http://localhost:5000/read';
      axios.get(path)
        .then((res) => {
          this.vms = res.data.vms;
        })
        .catch((error) => {

          console.error(error);
        });
    },
    handleAddReset() {
      this.initForm();
    },
    handleAddSubmit() {
      this.toggleAddVmModal();
      // let read = false;
      // if (this.addVMForm.read[0]) {
      //   read = true;
      // }
      const payload = {
        name: this.addVMForm.name,
        cpu: this.addVMForm.cpu,
        ram: this.addVMForm.ram,
      };
      this.addVm(payload);
      this.initForm();
    },
    initForm() {
      this.addVMForm.name = '';
      this.addVMForm.cpu = '';
      this.addVMForm.ram = '';
    },
    toggleAddVmModal() {
      const body = document.querySelector('body');
      this.activeAddVmModal = !this.activeAddVmModal;
      if (this.activeAddVmModal) {
        body.classList.add('modal-open');
      } else {
        body.classList.remove('modal-open');
      }
    },
    handleDeleteVm(vm) {
      this.removeVm(vm.name);
    },
    removeVm(vmID) {
      const path = `http://localhost:5000/delete/${vmID}`;
      axios.delete(path)
        .then(() => {
          this.getVMs();
          this.message = 'Vm removed!';
          this.showMessage = true;
        })
        .catch((error) => {
          console.error(error);
          thisMgetVms();
        });
    },


  },
  created() {
    this.getVMs();
  },
};
</script>



