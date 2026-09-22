import { motion } from 'framer-motion';
import { useAppConfig } from '@/contexts/AppConfigContext';

export const Greeting = () => {
  const { greeting } = useAppConfig();
  return (
    <div
      key="overview"
      className="mx-auto flex size-full max-w-3xl flex-col justify-center px-4 mb-6"
    >
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        className="font-display text-center text-2xl text-foreground"
      >
        {greeting}
      </motion.div>
    </div>
  );
};
