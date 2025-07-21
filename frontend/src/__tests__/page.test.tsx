import { render, screen } from '@testing-library/react';
import Home from '@/app/page';
import { AuthProvider } from '@/contexts/AuthContext';

// Mock the components
jest.mock('@/app/components/ClientOnly', () => {
  return function ClientOnly({ children }: { children: React.ReactNode }) {
    return <>{children}</>;
  };
});

jest.mock('@/app/components/AnimatedBackground', () => {
  return function AnimatedBackground() {
    return <div data-testid="animated-background">Animated Background</div>;
  };
});

jest.mock('@/components/Navigation', () => {
  return function Navigation() {
    return <nav data-testid="navigation">Navigation</nav>;
  };
});

const renderWithAuth = (component: React.ReactElement) => {
  return render(
    <AuthProvider>
      {component}
    </AuthProvider>
  );
};

describe('Home Page', () => {
  it('renders the main heading', () => {
    renderWithAuth(<Home />);
    
    expect(screen.getByText('Elimu')).toBeInTheDocument();
    expect(screen.getByText('Hub')).toBeInTheDocument();
    expect(screen.getByText('AI')).toBeInTheDocument();
  });

  it('renders the description text', () => {
    renderWithAuth(<Home />);
    
    expect(screen.getByText(/Empowering Kenyan education with AI/)).toBeInTheDocument();
  });

  it('renders navigation buttons', () => {
    renderWithAuth(<Home />);
    
    expect(screen.getByRole('link', { name: /Try Generative AI/ })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Knowledge Chat/ })).toBeInTheDocument();
  });

  it('renders navigation and animated background', () => {
    renderWithAuth(<Home />);
    
    expect(screen.getByTestId('navigation')).toBeInTheDocument();
    expect(screen.getByTestId('animated-background')).toBeInTheDocument();
  });
});
