<style lang="css">
.globalsearch {

}
.globalsearch-bj {
  background-color: #F8F8F8;
  border-radius: 15px;
  padding-left: 10px;
  padding-right: 5px;
  display: flex;
}
.globalsearch-bj input {
  background: transparent;
  height: 22px;
  margin-right: 3px;
  border: none;
  outline: none;
}
.globalsearch-bj span {
  margin-top: 3px;
  width: 16px;
  height: 16px;
  background: url('./../asset/image/main/search.png') no-repeat;
}
.globalsearch-bj span:hover {
  background: url('./../asset/image/main/search-hover.png') no-repeat;
}
</style>
<template lang="html">
  <span class="globalsearch" v-if="notStaff">
    <div class="globalsearch-bj">
      <input type="text" />
      <span></span>
    </div>
  </span>
</template>

<script>
export default {
  data () {
    return {
      notStaff: false
      //notStaff: this.$store.state.auth.access != 'staff'
    }
  }
}
</script>
