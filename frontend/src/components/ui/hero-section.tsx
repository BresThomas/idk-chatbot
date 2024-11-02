import { useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { buttonVariants } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { signInWithPopup, onAuthStateChanged, GithubAuthProvider } from 'firebase/auth';
import { auth } from '@/firebase/firebaseConfig';
import { useNavigate } from 'react-router-dom';

const Hero12 = () => {
  const navigate = useNavigate();
  const provider = new GithubAuthProvider(); // Utiliser GitHub comme fournisseur

  const handleLogin = async () => {
      try {
          const result = await signInWithPopup(auth, provider);
          console.log(result.user);
          navigate('/dashboard');
      } catch (error) {
          console.error(error);
      }
  };

  useEffect(() => {
      const unsubscribe = onAuthStateChanged(auth, (user) => {
          if (user) {
              navigate('/dashboard');
          }
      });

      return () => unsubscribe();
  }, [navigate]);

  return (
    <section className="relative overflow-hidden py-32">
      <div className="container">
        <div className="mx-auto flex max-w-5xl flex-col items-center">
          <div className="z-10 flex flex-col items-center gap-6 text-center">
            <img
              src="https://www.shadcnblocks.com/images/block/block-1.svg"
              alt="logo"
              className="h-16"
            />
            <Badge variant="outline">UI Blocks</Badge>
            <div>
              <h1 className="mb-6 text-pretty text-2xl font-bold lg:text-5xl">
                Build your next project with Blocks
              </h1>
              <p className="text-muted-foreground lg:text-xl">
                Lorem ipsum dolor sit amet consectetur adipisicing elit. Elig
                doloremque mollitia fugiat omnis! Porro facilis quo animi
                consequatur. Explicabo.
              </p>
            </div>
            <button
                className="px-4 py-2 text-white bg-blue-600 rounded"
                onClick={handleLogin}>
                Get Started
            </button>
            <div className="mt-20 flex flex-col items-center gap-4">
              <p className="text-center: text-muted-foreground lg:text-left">
                Built with open-source technologies
              </p>
              <div className="flex flex-wrap items-center justify-center gap-4">
                <a
                  href="#"
                  className={cn(
                    buttonVariants({ variant: 'outline' }),
                    'group px-3',
                  )}
                >
                  <img
                    src="https://www.shadcnblocks.com/images/block/logos/shadcn-ui-small.svg"
                    alt="company logo"
                    className="h-6 saturate-0 transition-all group-hover:saturate-100"
                  />
                </a>
                <a
                  href="#"
                  className={cn(
                    buttonVariants({ variant: 'outline' }),
                    'group px-3',
                  )}
                >
                  <img
                    src="https://www.shadcnblocks.com/images/block/logos/typescript-small.svg"
                    alt="company logo"
                    className="h-6 saturate-0 transition-all group-hover:saturate-100"
                  />
                </a>

                <a
                  href="#"
                  className={cn(
                    buttonVariants({ variant: 'outline' }),
                    'group px-3',
                  )}
                >
                  <img
                    src="https://www.shadcnblocks.com/images/block/logos/react-icon.svg"
                    alt="company logo"
                    className="h-6 saturate-0 transition-all group-hover:saturate-100"
                  />
                </a>
                <a
                  href="#"
                  className={cn(
                    buttonVariants({ variant: 'outline' }),
                    'group px-3',
                  )}
                >
                  <img
                    src="https://www.shadcnblocks.com/images/block/logos/tailwind-small.svg"
                    alt="company logo"
                    className="h-4 saturate-0 transition-all group-hover:saturate-100"
                  />
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero12;
