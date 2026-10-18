// Demo de pago por hitos en la testnet de Stellar.
//
// El comprador deposita el 100% en dos balances reclamables (30% y 70%).
// Solo el vendedor puede reclamarlos; si no lo hace, el comprador los
// recupera después del plazo. Qhatu no tiene llaves ni toca los fondos.
//
// Es una demo con XLM de prueba y balances reclamables nativos: no usa
// todavía el escrow de Trustless Work ni USDC. La verificación de los
// documentos de cada hito se simula acá; en el producto la haría el
// motor de reglas.
//
// Uso:
//   npm install
//   node demo.mjs          corre el flujo en la testnet (necesita red)
//   node demo.mjs --dry    arma las transacciones sin enviarlas
import { writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import {
  Account, Asset, BASE_FEE, Claimant, Horizon, Keypair, Networks,
  Operation, TransactionBuilder,
} from '@stellar/stellar-sdk'

const HORIZON = 'https://horizon-testnet.stellar.org'
const EXPLORADOR = 'https://stellar.expert/explorer/testnet/tx/'
const MONTO = 100
const HITOS = [
  { nombre: 'pedido confirmado', porcentaje: 30 },
  { nombre: 'guía de embarque verificada', porcentaje: 70 },
]
const DIAS_PLAZO = 7
const dry = process.argv.includes('--dry')

const monto = (pct) => ((MONTO * pct) / 100).toFixed(7)

function armarDeposito(compradorKey, vendedorKey, cuenta) {
  const venceEn = Math.floor(Date.now() / 1000) + DIAS_PLAZO * 24 * 3600
  const claimants = [
    new Claimant(vendedorKey.publicKey(), Claimant.predicateUnconditional()),
    // El comprador solo recupera después del plazo.
    new Claimant(
      compradorKey.publicKey(),
      Claimant.predicateNot(Claimant.predicateBeforeAbsoluteTime(String(venceEn))),
    ),
  ]
  const tx = new TransactionBuilder(cuenta, { fee: BASE_FEE, networkPassphrase: Networks.TESTNET })
  for (const h of HITOS) {
    tx.addOperation(Operation.createClaimableBalance({
      asset: Asset.native(), amount: monto(h.porcentaje), claimants,
    }))
  }
  const armada = tx.setTimeout(120).build()
  armada.sign(compradorKey)
  return armada
}

function armarReclamo(vendedorKey, cuenta, balanceId) {
  const tx = new TransactionBuilder(cuenta, { fee: BASE_FEE, networkPassphrase: Networks.TESTNET })
    .addOperation(Operation.claimClaimableBalance({ balanceId }))
    .setTimeout(120)
    .build()
  tx.sign(vendedorKey)
  return tx
}

async function fondear(publicKey) {
  const r = await fetch(`https://friendbot.stellar.org/?addr=${encodeURIComponent(publicKey)}`)
  if (!r.ok) throw new Error(`friendbot respondió ${r.status}`)
}

const comprador = Keypair.random()
const vendedor = Keypair.random()

if (dry) {
  const dep = armarDeposito(comprador, vendedor, new Account(comprador.publicKey(), '1'))
  const rec = armarReclamo(vendedor, new Account(vendedor.publicKey(), '1'), '0'.repeat(72))
  console.log('Modo --dry: no se envía nada.')
  console.log(`Depósito: ${dep.operations.length} operaciones, ${dep.toXDR().length} caracteres de XDR`)
  console.log(`Reclamo: ${rec.operations.length} operación, ${rec.toXDR().length} caracteres de XDR`)
  process.exit(0)
}

const server = new Horizon.Server(HORIZON)
console.log('1. Creando y fondeando las cuentas de prueba (friendbot)...')
await Promise.all([fondear(comprador.publicKey()), fondear(vendedor.publicKey())])

console.log(`2. El comprador deposita ${MONTO} XLM de prueba en 2 balances (30% y 70%)...`)
const dep = await server.submitTransaction(
  armarDeposito(comprador, vendedor, await server.loadAccount(comprador.publicKey())),
)

const balances = (await server.claimableBalances().claimant(vendedor.publicKey()).call()).records
const resultado = {
  red: 'testnet',
  comprador: comprador.publicKey(),
  vendedor: vendedor.publicKey(),
  deposito: dep.hash,
  liberaciones: [],
}

for (const h of HITOS) {
  const balance = balances.find((b) => Number(b.amount) === Number(monto(h.porcentaje)))
  if (!balance) throw new Error(`no encontré el balance del hito "${h.nombre}"`)
  console.log(`3. Hito "${h.nombre}" verificado (simulado): se libera el ${h.porcentaje}%...`)
  const rec = await server.submitTransaction(
    armarReclamo(vendedor, await server.loadAccount(vendedor.publicKey()), balance.id),
  )
  resultado.liberaciones.push({ hito: h.nombre, porcentaje: h.porcentaje, hash: rec.hash })
}

const destino = fileURLToPath(new URL('../../datos/testnet-resultado.json', import.meta.url))
writeFileSync(destino, JSON.stringify(resultado, null, 2) + '\n')

console.log('\nListo. Pega esto en el campo "Testnet:" de APEX:')
console.log(`Testnet: ${EXPLORADOR}${dep.hash}`)
console.log('\nTransacciones:')
console.log(`  Depósito:        ${EXPLORADOR}${dep.hash}`)
for (const l of resultado.liberaciones) console.log(`  Liberación ${l.porcentaje}%:   ${EXPLORADOR}${l.hash}`)
console.log(`\nGuardado en ${destino}`)
