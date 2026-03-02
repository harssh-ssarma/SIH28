/**
 * @deprecated Removed — contained JSX inside a hook (architecture violation).
 *
 * Replacement: <CardProgress ref={...} /> (forwardRef + useImperativeHandle)
 *   import { CardProgress, type CardProgressHandle } from '@/components/ui/CardProgress'
 *
 * Migration:
 *   BEFORE  const { start, finish, reset, BarElement } = useCardProgress()
 *           {BarElement}
 *
 *   AFTER   const ref = useRef<CardProgressHandle>(null)
 *           <CardProgress ref={ref} />
 *           ref.current?.start() / ref.current?.finish() / ref.current?.reset()
 */
export {}
