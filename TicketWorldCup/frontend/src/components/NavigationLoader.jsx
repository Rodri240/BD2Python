import { useNavigation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

export default function NavigationLoader() {
  const navigation = useNavigation();
  const loading = navigation.state === 'loading';

  return (
    <AnimatePresence>
      {loading && (
        <motion.div
          className="nav-loader"
          initial={{ scaleX: 0, opacity: 1 }}
          animate={{ scaleX: 1, opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          style={{ transformOrigin: 'left' }}
        />
      )}
    </AnimatePresence>
  );
}
