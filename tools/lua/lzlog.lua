-- Log every graphics decompression ($80:9A92: A = address, X = bank) with the caller's return address.
L.on_exec(0x809A92, 0x809A92, function()
  local s = emu.getState()
  local sp = s["cpu.sp"]
  local m = emu.memType.snesMemory
  local ret = emu.read(sp + 1, m) | emu.read(sp + 2, m) << 8 | emu.read(sp + 3, m) << 16
  local src = ((s["cpu.x"] & 0xFF) << 16) | s["cpu.a"]
  L.log(string.format("f%d lz src=%06X off=%06X ret=%06X", L.frame, src, L.rom_off(src), ret))
end)
