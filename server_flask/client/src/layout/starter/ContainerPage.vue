<script setup>
   import { store } from "../../main.js";
</script>
<template>
   <div class="container">
      <div class="row">
         <div class="col-sm-10">
            <h1>Containers</h1>
            <hr />
            <br /><br />
            <div v-for="(vmData, index) in containers" :key="index">
               <div v-for="(element, vmName) in vmData" :key="vmName">
                  <br /><br />
                  <h3>VM: {{vmName}}</h3>
                  <button
                     type="button"
                     class="btn btn-primary btn-sm"
                     >
                  Add Container
                  </button>
                  <table class="table table-hover">
                     <thead>
                        <tr>
                           <th scope="col">Container Name</th>
                           <th scope="col">Image</th>
                           <th scope="col">Status</th>
                           <th scope="col">Modify</th>
                           <th scope="col">Host Port</th>
                           <th scope="col">Container Port</th>
                           <th></th>
                        </tr>
                     </thead>
                     <tbody>
                        <tr v-for="(container, sus) in element" :key="sus">
                           <td>{{ container.name}}</td>
                           <td>{{ container.image}}</td>
                           <td>
                              <div style="display: flex; gap: 5px; align-items: center">
                                 {{ container.status }}
                                 <div>
                                    <button
                                       type="button"
                                       class="btn btn-link btn-success"
                                       >
                                    <i
                                       class="icon-play"
                                       style="font-style: normal; font-size: 20px"
                                       ></i>
                                    </button>
                                    <button
                                       type="button"
                                       class="btn btn-danger btn-link"
                                       >
                                    <i
                                       class="icon-stop"
                                       style="font-style: normal; font-size: 20px"
                                       ></i>
                                    </button>
                                    <button
                                       type="button"
                                       class="btn btn-warning btn-link"
                                       >
                                    <i
                                       class="icon-refresh-00"
                                       style="font-style: normal; font-size: 20px"
                                       ></i>
                                    </button>
                                 </div>
                              </div>
                           </td>
                           <td><button
                              type="button"
                              class="btn btn-danger btn-sm width-150px"
                              @click="handleDeleteVm(vm)"
                              >
                              Delete
                              </button>
                           </td>
                           <td>{{ container.vm_port }}</td>
                           <td>{{ container.container_port }}</td>
                        </tr>
                     </tbody>
                  </table>
               </div>
            </div>
         </div>
      </div>
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
         containers:[]
       };
     },
     methods: {
       addVm(payload) {
         const path = "http://localhost:5000/create";
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
         const path = `http://localhost:5000/update/${vmId}`;
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
         const path = "http://localhost:5000/read";
         axios
           .get(path)
           .then((res) => {
             this.vms = res.data.vms;
             return res.data.vms;
           })
           .catch((error) => {
             console.error(error);
           });
            
       },
   
       getContainers(){
           console.log("getcontainers")
           let containers=[];
           this.vms.forEach((vm)=>{
               console.log(vm.name)
             axios
               .get(`http://${vm.ip}:5002/read`)
               .then((res) => {
               containers.push(res.data)
                })
               .catch((error) => {
               console.error(error);
               });
           this.containers=containers
           console.log(this.containers)
           })
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
         const path = `http://localhost:5000/delete/${vmID}`;
         axios
           .delete(path)
           .then(() => {
             this.getVMs();
             this.message = "Vm removed!";
             this.showMessage = true;
           })
           .catch((error) => {
             console.error(error);
             this.getVMs();
           });
       },
       handleReloadVm(vm) {
         this.reloadVm(vm.name);
       },
       reloadVm(vmID) {
         const path = `http://localhost:5000/reload/${vmID}`;
         axios
           .post(path)
           .then(() => {
             this.getVMs();
             this.message = "Vm reloaded!";
             this.showMessage = true;
           })
           .catch((error) => {
             console.error(error);
             this.getVms();
           });
       },
       handleStartVm(vm) {
         this.startVm(vm.name);
       },
       startVm(vmID) {
         const path = `http://localhost:5000/start/${vmID}`;
         axios
           .post(path)
           .then(() => {
             this.getVMs();
             this.message = "Vm reloaded!";
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
         const path = `http://localhost:5000/stop/${vmID}`;
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
       console.log(this);
       this.getVMs();
       setTimeout(() => {
         this.getContainers(); // DA CAMBIARE
       }, 1000);
   },
   };
</script>