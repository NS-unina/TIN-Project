<script setup>
import { selectedVm } from "../../main.js";
</script>

<template>

  <div class="container">

    <div class="row">
      <div class="col-sm-10">
        <h1>TIN PROJECT</h1>
        <hr />
        <br /><br />
       
        <div class="row">
                <div class="col-md-5 ml-auto">
                  <div class="info-area info-horizontal mt-10">
                    <div class="icon icon-warning">
                      <i class="tim-icons  icon-bulb-63" style="font-style: normal; font-size: 50px"></i>
                    </div>
                    <div class="description">
                      <h3 class="info-title" style="margin-bottom: 5px;">Intuitive</h3>
                      <p class="description">
                        Easily manage and monitor your virtual machines, containers and services, with an intuitive layout and easy navigation
                      </p>
                    </div>
                  </div>
                  <div class="info-area info-horizontal">
                    <div class="icon icon-primary" style="font-style: normal; font-size: 50px">
                      <i class="tim-icons icon-zoom-split"></i>
                    </div>
                    <div class="description">
                      <h3 class="info-title" style="margin-bottom: 5px;">Informative</h3>
                      <p class="description">
                    Stay informed of real-time insights about usage and status at a glance, all in one intuitive dashboard
                      </p>
                    </div>
                  </div>
                  <div class="info-area info-horizontal">
                    <div class="icon icon-primary" style="font-style: normal; font-size: 50px">
                      <i class="tim-icons icon-lock-circle"></i>
                    </div>
                    <div class="description">
                      <h3 class="info-title" style="margin-bottom: 5px;">Secure</h3>
                      <p class="description">
                        Protected by Auth0 and Okta
                      </p>
                    </div>
                  </div>
                </div>
                <div class=" col-md-5 ml-auto ">
                 
                      <div class="card card-register  ">
                        <!---->
                        <div class="card-header">
                            <img
                            src="img/honeycomb.png"
                            alt="Card image"
                            class="card-img"
                          />
                          
                          <h4 class="card-title">Get Started</h4>
                        </div>
                        <div class="card-body">
                           <LoginButton />                        
                        </div>
                      </div>
                  
                </div>
              </div>







    </div>
    </div>

    
  </div>
</template>

<script>
import LoginButton from "@/components/Buttons/login-button.vue";

</script>
