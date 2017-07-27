<template>
  <div class="request">
    <div id="cloud-img-wrapper">
      <img id="cloud-img" src="../assets/cloud.png">
      <h3><i-count-up :start="0" :end="num_images" :duration="3.5"></i-count-up> images retrieved from <span class="bold-italics">the cloud.</span></h3>
    </div>
  </div>
</template>

<script>
/*
import _ from 'lodash'
*/
import axios from 'axios'
import ICountUp from 'vue-countup-v2'
export default {
  name: 'search',
  props: ['query'],
  components: { ICountUp },
  data () {
    return {
      query: this.query,
      num_images: 0
    }
  },
  methods: {
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.request {
  display: flex;
  justify-content: space-around;
}

#cloud-img-wrapper {
 height: 350px;
 width: 503px;
 padding-top: 50px;
 position: relative;
}

#cloud-img {
  height: 300px;
}

h3 {
  position: absolute;
  top: 245px;
  text-align: center;
  left: 0;
  margin: 0 auto;
  width: 100%;
}

.bold-italics {
  font-style: italic;
}

.request-inner {
  text-align: center;
  margin-top: 100px;
}
</style>
