setInterval(() => {
  for(let y = 0; y < 16; y++) {
    for(let x = 0; x < 16; x++) {
      process.stdout.write(Buffer.allocUnsafe(8).fill(Math.floor(Math.random() * 255), undefined, undefined, "raw"));
    }
  }
}, 10);
