<script setup>
   import { selectedContainer } from "../../main.js";
</script>
<template>
   <div class="container">
      <div class="row">
         <div class="col-sm-10">
            <h1>Containers</h1>
            <hr />
            <br /><br />
            <div v-for="(vmData, index) in vms" :key="index">


              <div><h3 style="display: inline;">VM: {{vmData.name}}</h3> <h5 style="display: inline;">IP: {{vmData.ip}}</h5></div>
              <button
                     type="button"
                     class="btn btn-primary btn-sm"
                     @click="(selectedContainer.containerIp = vmData[vmName][0].ip), toggleAddContainerModal()"

                     >
                  Add Container
                  </button>
                  
                  <div v-for="(containers, vmName) in grouped_containers" :key="vmName">

                  <div v-if="vmName === vmData.name"> 
                  <table  class="table table-hover" >
                    
                     <thead>
                        <tr>
                           <th scope="col">Container Name</th>
                           <th scope="col">Image</th>
                           <th scope="col">Status</th>
                           <th scope="col">Controls</th>
                           <th scope="col">Modify</th>
                           <th scope="col">Services </th>

                        </tr> 
                     </thead>
                     <tbody>
          <tr v-for="container in containers" :key="container.name">


            <td>{{ container.name }}</td>
            <td>{{ container.image }}</td>
            <td>{{ container.status }}</td>

             <td>
                              <div style="display: flex; gap: 5px; align-items: center">
                                 <div>
                                    <button
                                       type="button"
                                       class="btn btn-link btn-success"
                                       @click="handleStartContainer(container.name,vmData[vmName][0].ip)"

                                       >
                                    <i
                                       class="icon-play"
                                       style="font-style: normal; font-size: 20px"
                                       ></i>
                                    </button>
                                    <button
                                       type="button"
                                       class="btn btn-danger btn-link"
                                       @click="handleStopContainer(container.name,vmData[vmName][0].ip)"

                                       >
                                    <i
                                       class="icon-stop"
                                       style="font-style: normal; font-size: 20px"
                                       ></i>
                                    </button>
                                    <button
                                       type="button"
                                       class="btn btn-warning btn-link"
                                       @click="handleReloadContainer(container.name,vmData[vmName][0].ip)"

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
                              @click="handleDeleteContainer(container.name,vmData[vmName][0].ip)"
                              >
                              Delete
                              </button>
                           </td>             

                           <td>

                      
                                <tr v-for="service in container.services" :key="service.name">
                                  
                                
                            
                                  <td >{{ service.name }}</td>
                                  <td v-show="showColumns">{{ service.service_port }}</td>
                                  <td v-show="showColumns">{{ service.container_port }}</td>
                                  <td v-show="showColumns">{{ service.priority }}</td>
                                  <td v-show="showColumns">{{ service.vm_port }}</td>
                                  <td v-show="showColumns">{{ service.busy }}</td>
                                </tr>
                          </td>
                              





          </tr>
        </tbody>
          </table>
        </div>
        </div>


               <!-- <div v-for="(element, vmName) in vmData" :key="vmName">
                  <br /><br />
                  <h3>VM: {{vmName}}</h3> 
                  
                  <button
                     type="button"
                     class="btn btn-primary btn-sm"
                     @click="(selectedContainer.containerIp = vmData[vmName][0].ip), toggleAddContainerModal()"

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
                                       @click="handleStartContainer(container.name,vmData[vmName][0].ip)"

                                       >
                                    <i
                                       class="icon-play"
                                       style="font-style: normal; font-size: 20px"
                                       ></i>
                                    </button>
                                    <button
                                       type="button"
                                       class="btn btn-danger btn-link"
                                       @click="handleStopContainer(container.name,vmData[vmName][0].ip)"

                                       >
                                    <i
                                       class="icon-stop"
                                       style="font-style: normal; font-size: 20px"
                                       ></i>
                                    </button>
                                    <button
                                       type="button"
                                       class="btn btn-warning btn-link"
                                       @click="handleReloadContainer(container.name,vmData[vmName][0].ip)"

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
                              @click="handleDeleteContainer(container.name,vmData[vmName][0].ip)"
                              >
                              Delete
                              </button>
                           </td>
                           <td>{{ container.vm_port }}</td>
                           <td>{{ container.container_port }}</td>
                        </tr>
                     </tbody>
                  </table>
               </div> -->
            </div>

            <!-- add new container modal -->
    <div
      ref="addContainerModal"
      class="modal fade"
      :class="{ show: activeAddContainerModal, 'd-block': activeAddContainerModal }"
      tabindex="-1"
      role="dialog"
    >
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add a new Container</h5>
            <button
              type="button"
              class="close"
              data-dismiss="modal"
              aria-label="Close"
              @click="(selectedContainer.containerIp = ''),toggleAddContainerModal()"
            >
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <form>
              <div class="mb-3">
                <label for="addContainerName" class="form-label">Name:</label>
                <input
                  type="text"
                  style="color: black"
                  class="form-control"
                  id="addContainerName"
                  v-model="addContainerForm.name"
                  placeholder="Enter name of the Container"
                />
              </div>
              <div class="mb-3">
                <label for="addContainerImage" class="form-label">Image:</label>
                <input
                  type="text"
                  style="color: black"
                  class="form-control"
                  id="addContainerImage"
                  v-model="addContainerForm.image"
                  placeholder="Enter name of the image"
                />
              </div>
              <div class="mb-3">
                <label for="addContainerVmPort" class="form-label">Vm_Port:</label>
                <input
                  type="text"
                  style="color: black"
                  class="form-control"
                  id="addContainerVmPort"
                  v-model="addContainerForm.vm_port"
                  placeholder="Enter the VM port to expose the service"
                />
              </div>


              <div class="btn-group" role="group">
                <button
                  type="button"
                  class="btn btn-primary btn-sm"
                  @click="handleAddSubmit(selectedContainer.containerIp)"
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

         </div>
      </div>
   </div>
</template>
<script>
   import axios from "axios";

   export default {
     data() {
       return {
         activeAddContainerModal: false,
         activeUpdateContainerModal: false,
         addContainerForm: {
           name: "",
           image: "",
           vm_port: "",

         },

         vms: [],
         containers:[],
         grouped_containers:{}
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
         const path = "http://localhost:5000/vm/list";
         axios
           .get(path)
           .then((res) => {
             this.vms = res.data;
             console.log(res.data)
             return res.data;
           })
           .catch((error) => {
             console.error(error);
           });
       },
   
       getContainers(){
           console.log("getcontainers")
           let containers=[];
           let response


          //  for vm in vmList:
          //   if vm["status"] == "running":                               #[FIXME] e se la vm è accesa ma container configurator non è running?
          //       IP_CONTAINER_MASTER = vm["ip"]
          //       print ("Container Master: ",IP_CONTAINER_MASTER)
          //       break
           let container_master_ip=""
           this.vms.forEach((vm)=>{
               console.log(vm.status)
               if (vm.status=="running"){
                console.log(vm.name)
                container_master_ip=vm.ip
               } })

             axios
             .get(`http://127.0.0.1:5002/container/list`)
            //  .get(`http://${container_master_ip}:5002/container/list`)
             .then((res) => {
               response=res.data
               //console.log(res.data)
              //  res.data.forEach((container)=>{
              //   console.log(container.name)
              //  })
                const groupedData = response.reduce((acc, item) => {
                  const key = item["vm_name"]; // Get the grouping key value
                  if (!acc[key]) {
                    acc[key] = []; // Initialize array if not exists
                  }

                  const vm = this.vms.find(vm => vm.name === item.vm_name);
                  if (vm) {
                    item.ip = vm.ip; // Add the IP address to the item
                  }
                  acc[key].push(item);
                  return acc;
                }, {});
                this.grouped_containers=groupedData
                console.log(this.grouped_containers)
                })
               .catch((error) => {
               console.error(error);
               });
          //  this.containers=containers
          //  console.log(this.containers)
          
       },
   
       handleAddReset() {
         this.initAddForm();
       },
  
       handleAddSubmit(ip) {
        console.log(ip)
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
         const path = `http://${ip}:5002/delete/${name}`;
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
         const path = `http://${ip}:5002/stop/${name}`;
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