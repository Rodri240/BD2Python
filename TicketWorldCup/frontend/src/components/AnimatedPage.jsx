import { motion } from 'framer-motion';
import { pageVariants, pageTransition, spring } from './animationVariants';

export function AnimatedPage({ children, className }) {
  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={pageTransition}
      className={className}
    >
      {children}
    </motion.div>
  );
}

export function MotionCard({ children, className, ...props }) {
  return (
    <motion.div
      className={className}
      whileHover={{ y: -2, boxShadow: '0 8px 24px rgba(0,0,0,0.35)' }}
      transition={spring}
      {...props}
    >
      {children}
    </motion.div>
  );
}

export function MotionBtn({ children, className, ...props }) {
  return (
    <motion.button
      className={className}
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.96 }}
      transition={spring}
      {...props}
    >
      {children}
    </motion.button>
  );
}
