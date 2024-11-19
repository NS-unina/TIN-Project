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
                  <h3>VM: {{vmName}} <h4>{{containers}}</h4> </h3> 
                  

                  <button
                     type="button"
                     class="btn btn-primary btn-sm"
                     @click="handleAddSubmit(vmData.ip)"

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
                                       @click="handleStartContainer(container.name,vmData.ip)"

                                       >
                                    <i
                                       class="icon-play"
                                       style="font-style: normal; font-size: 20px"
                                       ></i>
                                    </button>
                                    <button
                                       type="button"
                                       class="btn btn-danger btn-link"
                                       @click="handleStopContainer(container.name,vmData.ip)"

                                       >
                                    <i
                                       class="icon-stop"
                                       style="font-style: normal; font-size: 20px"
                                       ></i>
                                    </button>
                                    <button
                                       type="button"
                                       class="btn btn-warning btn-link"
                                       @click="handleReloadContainer(container.name,vmData.ip)"

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
                              @click="handleDeleteContainer(container.name,vmData.ip)"
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
         addContainerForm: {
           name: "",
           image: "",
           vm: "",
           ip: "",
         },

         vms: [],
         containers:[]
       };
     },
     methods: {
       addContainer(ip,payload) {
         const path = `http://${ip}:5002/create`;
         axios
           .post(path, payload)
           .then(() => {
             this.getContainers();
           })
           .catch((error) => {
             console.log(error);
             this.getContainers();
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
           let response
           let i=0
           this.vms.forEach((vm)=>{
               console.log(vm.name)
             axios
               .get(`http://${vm.ip}:5002/read`)
               .then((res) => {
               response=res.data
               for (let key in response){
                console.log(key)
                for (let element in response[key]){
                response[key][element].ip=vm.ip}
               }
            //    container.ip=vm.ip
               containers.push(response)
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
  
       handleAddSubmit(ip) {
         this.toggleAddContainerModal();
         // let read = false;
         // if (this.addVMForm.read[0]) {
         //   read = true;
         // }
         const payload = {
           name: this.addContainerForm.name,
           image: this.addContainerForm.image,
           vm_port: this.addContainerForm.vm_port,
         };
         this.addContainer(ip,payload);
         this.initAddForm();
       },
      
       initAddForm() {
         this.addContainerForm.name = "";
         this.addContainerForm.image = "";
         this.addContainerForm.vm_port = "";
       },
    
       toggleAddContainerModal() {
         const body = document.querySelector("body");
         this.activeAddContainerModal = !this.activeAddContainerModal;
         if (this.activeAddContainerModal) {
           body.classList.add("modal-open");
         } else {
           body.classList.remove("modal-open");
         }
       },
      
   
       handleDeleteContainer(name,ip) {
         this.removeContainer(name,ip);
       },
       removeContainer(name,ip) {
         const path = `http://${ip}:5000/delete/${name}`;
         axios
           .delete(path)
           .then(() => {
             this.getContainers();
             this.message = "Container removed!";
             this.showMessage = true;
           })
           .catch((error) => {
             console.error(error);
             this.getContainers();
           });
       },
       handleReloadContainer(name,ip) {
         this.reloadContainer(name,ip);
       },
       reloadContainer(name,ip) {
         const path = `http://${ip}:5002/reload/${name}`;
         axios
           .post(path)
           .then(() => {
             this.getContainers();
             this.message = "Container reloaded!";
             this.showMessage = true;
           })
           .catch((error) => {
             console.error(error);
             this.getContainers();
           });
       },
       handleStartContainer(name,ip) {
         this.startContainer(name,ip);
       },
       startContainer(name,ip) {
            console.log(name,ip)
         const path = `http://${ip}:5002/start/${name}`;
         axios
           .post(path)
           .then(() => {
             this.getContainers();
             this.message = "Container Started!";
             this.showMessage = true;
           })
           .catch((error) => {
             console.error(error);
             this.getContainers();
           });
       },
       handleStopContainer(name,ip) {
         this.stopContainer(name,ip);
       },
       stopContainer(name,ip) {
         const path = `http://${ip}:5000/stop/${name}`;
         axios
           .post(path)
           .then(() => {
             this.getContainers();
             this.message = "Container stopped!";
             this.showMessage = true;
           })
           .catch((error) => {
             console.error(error);
             this.getContainers();
           });
       },
     },
     created() {
       console.log(this);
       this.getVMs();
       setTimeout(() => {
         this.getContainers(); // DA CAMBIARE (concatenare)
       }, 1000);
   },
   };
</script>