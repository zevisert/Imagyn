<template>
  <div class="request">
    <div id="img-wrapper" :class="{ tform : transform_stage}">
      <template v-if="!errored">
        <template v-if="transform_stage">
          <h1>Synthesizing Images!</h1>
          <img id="img-img" :class="current_animation" src="../assets/toucan-polaroid.jpg">
        </template>
        <template v-else>
          <img id="cloud-img" src="../assets/cloud.png">
          <template v-if="download_complete">
            <h3>
              <i-count-up :start="0" :end="num_images" :duration="3.5"></i-count-up> images retrieved from <span class="bold-italics">the cloud</span>.
            </h3>
          </template>
          <template v-else>
            <h3>
              Downloading images from <span class="bold-italics">the cloud</span><span class="dots">{{ dots }}</span>
            </h3>
          </template>
        </template>
      </template>
      <template v-else>
        <h3>
          Error!
        </h3>
      </template>
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
  mounted: function () {
    let dotInc = setInterval(() => {
      this.dot_ticker++
      switch (this.dot_ticker % 3) {
        case 0:
          this.dots = '.'
          break
        case 1:
          this.dots = '..'
          break
        case 2:
          this.dots = '...'
          break
        default:
          this.dots = '.'
          break
      }
    }, 1000)
    this.$nextTick(function () {
      axios.get('http://localhost:5000/api/download/' + this.query)
      .then(response => {
        clearInterval(dotInc)
        this.download_complete = true
        this.num_images = response.data.num_images
        this.tmp_dir = response.data.dirname
        setTimeout(this.doTransforms(), 3000)
      })
      .catch(() => {
        clearInterval(dotInc)
        this.errored = true
      })
    })
  },
  components: { ICountUp },
  data () {
    return {
      num_images: 0,
      tmp_dir: '',
      dot_ticker: 0,
      dots: '.',
      errored: false,
      current_animation: 'ani_r',
      transform_stage: false,
      download_complete: false
    }
  },
  methods: {
    doTransforms: function () {
      this.transform_stage = true
      this.dot_ticker = 0
      setInterval(() => {
        this.dot_ticker++
        switch (this.dot_ticker % 3) {
          case 0:
            this.current_animation = 'ani_r'
            break
          case 1:
            this.current_animation = 'ani_f'
            break
          case 2:
            this.current_animation = 'ani_s'
            break
          default:
            this.current_animation = 'ani_r'
            break
        }
      }, 2500)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.request {
  display: flex;
  justify-content: space-around;
}

#img-wrapper {
 height: 350px;
 width: 503px;
 padding-top: 350px;
 position: relative;
 text-align: center;
}

#img-wrapper.tform {
  padding-top: 250px;
}

#cloud-img {
  height: 300px;
}

#img-img {
  margin-top: 40px;
  height: 400px;
  animation-duration: 2s;
  animation-delay: 0.5s;
  animation-timing-function: ease-in-out;
  border: 1.5px solid gray;
}

h3 {
  position: absolute;
  top: 545px;
  text-align: center;
  left: 0;
  margin: 0 auto;
  width: 100%;
}

.ani_r {
  animation: rotate;
}

.ani_s {
  animation: stretch;
}

.ani_f {
  animation: flip;
}

@keyframes rotate {
  0% {transform: rotate(0deg)}
  100% {transform: rotate(360deg)}
}

@keyframes flip {
  0% {transform: rotateY(0deg)}
  50% {transform: rotateY(180deg)}
  100% {transform: rotateY(0deg)}
}

@keyframes stretch {
  0% {transform: scale(1,1)}
  25% {transform: scale(0.5, 1)}
  75% {transform: scale(1, 0.5)}
  100% {transform: scale(1,1)}
}

.dots {
  width: 32px;
  text-align: left;
  display: inline-block;
}
.bold-italics {
  font-style: italic;
}

.request-inner {
  text-align: center;
  margin-top: 100px;
}
</style>
