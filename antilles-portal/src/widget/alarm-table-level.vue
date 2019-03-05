<style lang="css">
.alarm-level {
  display: inline-block;
  border-radius: 4px;
  text-transform:capitalize;
  color:#fff;
  font-size: 12px;
}
.alarm-level-normal {
  width: 50px;
  height: 24px;
}
.alarm-level-small {
  width: 12px;
  height: 12px;
}
.alarm-level-fatal {
  background: #ff6666;
}
.alarm-level-error {
  background: #ff7733;
}
.alarm-level-warn {
  background: #ffab00;
}
.alarm-level-info {
  background: #00c8f2;
}
</style>
<template lang="html">
  <p :title="levelTitle"
  :class="[ 'alarm-level', levelSize, leverColor ]">{{ $t('Alarm.PolicyLevel.'+ level) }}</p>
</template>

<script>
export default {
  data () {
    return {
      levelSize: 'alarm-level-' + this.alarmLevelSize,
      leverColor: 'alarm-level-' + this.alarmLevel,
      level: this.alarmLevelSize=='small'?'':this.alarmLevel,
      levelTitle: this.alarmLevelSize=='small'?this.alarmLevel:''
    }
  },
  props: [
    'alarmLevelSize',
    'alarmLevel'
  ]

}
</script>
