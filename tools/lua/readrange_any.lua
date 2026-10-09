-- Log unique PCs (with A/X/Y) that read CPU range LO..HI (globals; both banks $00 and $80 mirrors are hooked).
-- Usage: prepend "LO=0x00B84C HI=0x00B92A" to a copy of this file and pass it with emu.py --script.
local seen = {}
local function hook(addr, value)
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  if not seen[pc] then
    seen[pc] = true
    L.log(string.format("f%d pc=%06X read %06X A=%04X X=%04X Y=%04X DB=%02X", L.frame, pc, addr, s["cpu.a"],
      s["cpu.x"], s["cpu.y"], s["cpu.dbr"]))
  end
end
for _, mirror in ipairs({ 0, 0x800000 }) do
  emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, LO + mirror, HI + mirror, emu.cpuType.snes,
    emu.memType.snesMemory)
end
