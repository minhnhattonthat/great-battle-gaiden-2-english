-- Log dialogue box state at each glyph draw ($88:A1A4): VRAM dest, row/col counters, line width, colour, message id.
local m = emu.memType.snesMemory
local function w(a) return emu.read(a, m) | emu.read(a + 1, m) << 8 end
L.on_exec(0x88A1A4, 0x88A1A4, function()
  L.log(string.format("f%d 1E12=%04X 1E0D=%02X 0F98=%02X 0F99=%02X 0F9F=%04X 1E0E=%04X 1E10=%04X 1E08=%04X 1E0A=%04X",
    L.frame, w(0x1E12), emu.read(0x1E0D, m), emu.read(0x0F98, m), emu.read(0x0F99, m), w(0x0F9F), w(0x1E0E),
    w(0x1E10), w(0x1E08), w(0x1E0A)))
end)
