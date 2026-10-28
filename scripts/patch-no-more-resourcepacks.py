#!/usr/bin/env python3
"""Apply the NoMoreResourcePacks behavior to the Eaglercraft 26.2 source.

This deliberately changes the client packet handler: it acknowledges a server pack
push without calling DownloadedPackSource, so the browser never downloads/reloads
the server-provided resource pack.
"""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: patch-no-more-resourcepacks.py /path/to/ClientCommonPacketListenerImpl.java")

path = Path(sys.argv[1])
source = path.read_text(encoding="utf-8")

start_marker = "   @Override\n   public void handleResourcePackPush(final ClientboundResourcePackPushPacket packet) {"
end_marker = "   @Override\n   public void handleResourcePackPop(final ClientboundResourcePackPopPacket packet) {"

start = source.find(start_marker)
if start < 0:
    if "[NoMoreResourcePacks]" in source and "Action.SUCCESSFULLY_LOADED" in source:
        print(f"Already patched: {path}")
        raise SystemExit(0)
    raise SystemExit(f"Could not locate handleResourcePackPush in {path}")

end = source.find(end_marker, start)
if end < 0:
    raise SystemExit(f"Could not locate handleResourcePackPop after resource-pack push handler in {path}")

replacement = """   @Override
   public void handleResourcePackPush(final ClientboundResourcePackPushPacket packet) {
      PacketUtils.ensureRunningOnSameThread(packet, this, this.minecraft.packetProcessor());
      UUID packId = packet.id();

      // Match NoMoreResourcePacks: acknowledge the required pack without starting
      // DownloadedPackSource, avoiding browser CORS/download/reload failures.
      // ACCEPTED is sent before SUCCESSFULLY_LOADED, following the protocol flow.
      this.connection.send(new ServerboundResourcePackPacket(
         packId, ServerboundResourcePackPacket.Action.ACCEPTED
      ));
      this.connection.send(new ServerboundResourcePackPacket(
         packId, ServerboundResourcePackPacket.Action.SUCCESSFULLY_LOADED
      ));
      LOGGER.info("[NoMoreResourcePacks] Skipped server resource pack (id={}, required={})",
         packId, packet.required());
   }

"""

patched = source[:start] + replacement + source[end:]
path.write_text(patched, encoding="utf-8")
print(f"Patched {path}: resource-pack pushes are acknowledged without download")
